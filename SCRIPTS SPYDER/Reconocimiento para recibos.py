import cv2
import numpy as np
from ultralytics import YOLO
from scipy.optimize import linear_sum_assignment
import pandas as pd
import time
import os

def interpolate_cross_time(prev_y, curr_y, prev_t, curr_t, line_y):
    """Interpela el instante exacto de cruce de una línea."""
    if curr_y == prev_y:
        return curr_t
    fraction = (line_y - prev_y) / (curr_y - prev_y)
    return prev_t + fraction * (curr_t - prev_t)

###########################################
# Configuración y carga del modelo YOLOv8
###########################################
model = YOLO('yolov8n.pt')
# Sobreescribir la clase 3 a "motorbike" (opcional)
if hasattr(model, "names"):
    model.names[3] = "motorbike"

# Abrir el video (ejemplo: 1280x720)
video_path = r"C:\Users\TRAPPIST\Desktop\Detección de Velocidad\velocity.mp4"
cap = cv2.VideoCapture(video_path)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Resolución del video: {frame_width}x{frame_height}")

###########################################
# Parámetros de tracking y líneas de referencia
###########################################
max_inactive_frames = 10

# Cada track almacenará:
# - 'positions': lista de tuplas (center_x, center_y, t)
# - 'bbox': [x1, y1, x2, y2]
# - 'first_line_crossed': instante interpolado del cruce de la primera línea
# - 'second_line_crossed': instante interpolado del cruce de la segunda línea
# - 'frozen_speed': velocidad calculada
# - 'inactive_frames': contador de frames sin asignación
# - 'recorded': flag para evitar duplicados
# - 'vehicle_type': nombre del vehículo, obtenido de model.names
object_tracks = {}
next_track_id = 0
fps = cap.get(cv2.CAP_PROP_FPS)

# Líneas horizontales (como en tu código original)
line1_y = 400  # Primera línea
line2_y = 450  # Segunda línea
line_x_start = 565
line_x_end = 847
line1_start = (line_x_start, line1_y)
line1_end   = (line_x_end, line1_y)
line2_start = (line_x_start, line2_y)
line2_end   = (line_x_end, line2_y)

# Factor de conversión (píxeles -> metros)
meters_per_pixel = 0.05

# DataFrame y carpeta para el CSV (se añade la columna "Vehicle Type")
speed_records = pd.DataFrame(columns=['Track ID', 'Vehicle Type', 'Speed (km/h)', 'Timestamp'])
csv_directory = r"C:\Users\TRAPPIST\Desktop\Detección de Velocidad\CSVDATOS"
os.makedirs(csv_directory, exist_ok=True)
output_csv_path = os.path.join(csv_directory, 'Registro_Velocidades.csv')

###########################################
# Bucle principal
###########################################
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Tomar el instante de este frame
    frame_time = time.time()

    # Dibujar las líneas horizontales
    cv2.line(frame, line1_start, line1_end, (255, 255, 0), 2)
    cv2.line(frame, line2_start, line2_end, (0, 255, 255), 2)

    # Detección con YOLO con umbral de confianza (conf=0.5)
    results = model(frame, conf=0.5)
    current_detections = []
    # Cada detección se almacenará con: [center_x, center_y, x1, y1, x2, y2, cls, t]
    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])
            if cls in [1, 2, 3, 5, 7]:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                center_x = (x1 + x2) // 2
                center_y = y2  # Centro inferior
                current_detections.append([center_x, center_y, x1, y1, x2, y2, cls, frame_time])
                cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
                print(f"[Detección] Centro inferior: ({center_x}, {center_y}) | Clase: {cls} at t={frame_time:.2f}")

    ###########################################
    # Seguimiento: Asignación con Hungarian
    ###########################################
    updated_tracks = {}
    assigned_track_ids = set()
    if object_tracks:
        cost_matrix = np.zeros((len(object_tracks), len(current_detections)), dtype=np.float32)
        track_ids = list(object_tracks.keys())
        for i, tid in enumerate(track_ids):
            last_pos = object_tracks[tid]['positions'][-1][:2]  # (cx, cy)
            for j, detection in enumerate(current_detections):
                cost_matrix[i, j] = np.linalg.norm(np.array(last_pos) - np.array(detection[:2]))
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        for i in range(len(row_ind)):
            tid = track_ids[row_ind[i]]
            detection_idx = col_ind[i]
            prev_entry = object_tracks[tid]['positions'][-1]  # (cx, cy, t)
            curr_det = current_detections[detection_idx]         # [cx, cy, x1, y1, x2, y2, cls, t]
            curr_center = (curr_det[0], curr_det[1])
            object_tracks[tid]['positions'].append((curr_center[0], curr_center[1], curr_det[7]))
            object_tracks[tid]['bbox'] = curr_det[2:6]
            object_tracks[tid]['inactive_frames'] = 0
            assigned_track_ids.add(tid)

            prev_y = prev_entry[1]
            curr_y = curr_center[1]
            prev_t = prev_entry[2]
            curr_t = curr_det[7]
            print(f"[Track {tid}] prev_y: {prev_y}, curr_y: {curr_y}")

            # Registro de cruce de la primera línea con interpolación
            if object_tracks[tid].get('first_line_crossed') is None:
                if (prev_y < line1_y and curr_y >= line1_y) or (prev_y > line1_y and curr_y <= line1_y):
                    cross_t = interpolate_cross_time(prev_y, curr_y, prev_t, curr_t, line1_y)
                    object_tracks[tid]['first_line_crossed'] = cross_t
                    print(f"[Track {tid}] Cruzó línea 1 en t={cross_t:.3f}")

            # Registro de cruce de la segunda línea con interpolación
            if object_tracks[tid].get('first_line_crossed') is not None and object_tracks[tid].get('second_line_crossed') is None:
                if (prev_y < line2_y and curr_y >= line2_y) or (prev_y > line2_y and curr_y <= line2_y):
                    cross_t = interpolate_cross_time(prev_y, curr_y, prev_t, curr_t, line2_y)
                    object_tracks[tid]['second_line_crossed'] = cross_t
                    delta_t = cross_t - object_tracks[tid]['first_line_crossed']
                    print(f"[Track {tid}] Cruzó línea 2 en t={cross_t:.3f}. Delta_t: {delta_t:.3f} s")
                    if delta_t > 0:
                        displacement = abs(line2_y - line1_y) * meters_per_pixel
                        speed_kmh = (displacement / delta_t) * 3.6
                        speed_kmh = min(speed_kmh, 200)
                        object_tracks[tid]['frozen_speed'] = speed_kmh
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        cls_idx = current_detections[detection_idx][6]
                        vehicle_type = model.names[cls_idx] if cls_idx in model.names else "unknown"
                        new_record = pd.DataFrame({
                            'Track ID': [tid],
                            'Vehicle Type': [vehicle_type],
                            'Speed (km/h)': [speed_kmh],
                            'Timestamp': [timestamp]
                        })
                        speed_records = pd.concat([speed_records, new_record], ignore_index=True)
                        object_tracks[tid]['recorded'] = True
                        print(f"[Track {tid}] Velocidad calculada: {speed_kmh:.1f} km/h a las {timestamp} | Tipo: {vehicle_type}")
            updated_tracks[tid] = object_tracks[tid]

        # Incrementar inactividad para tracks no asignados en este frame
        for tid in object_tracks:
            if tid not in assigned_track_ids:
                object_tracks[tid]['inactive_frames'] += 1
                updated_tracks[tid] = object_tracks[tid]
    else:
        updated_tracks = {}

    # Crear nuevos tracks para detecciones no asignadas
    assigned_detection_indices = set(col_ind) if object_tracks else set()
    for j, detection in enumerate(current_detections):
        if j not in assigned_detection_indices:
            cls_idx = detection[6]
            vehicle_type = model.names[cls_idx] if cls_idx in model.names else "unknown"
            updated_tracks[next_track_id] = {
                'positions': [(detection[0], detection[1], detection[7])],
                'bbox': detection[2:6],
                'first_line_crossed': None,
                'second_line_crossed': None,
                'frozen_speed': None,
                'inactive_frames': 0,
                'recorded': False,
                'vehicle_type': vehicle_type
            }
            next_track_id += 1

    object_tracks = updated_tracks

    # Forzar el cruce de la segunda línea para tracks inactivos
    tracks_to_delete = []
    for tid, track in object_tracks.items():
        if track.get('inactive_frames', 0) >= max_inactive_frames:
            if track.get('first_line_crossed') is not None and track.get('second_line_crossed') is None:
                if not track.get('recorded', False):
                    track['second_line_crossed'] = time.time()  # sin interpolación ya que no hay actualización
                    delta_t = track['second_line_crossed'] - track['first_line_crossed']
                    if delta_t > 0:
                        displacement = abs(line2_y - line1_y) * meters_per_pixel
                        speed_kmh = (displacement / delta_t) * 3.6
                        speed_kmh = min(speed_kmh, 200)
                        track['frozen_speed'] = speed_kmh
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        vehicle_type = track.get('vehicle_type', "unknown")
                        new_record = pd.DataFrame({
                            'Track ID': [tid],
                            'Vehicle Type': [vehicle_type],
                            'Speed (km/h)': [speed_kmh],
                            'Timestamp': [timestamp]
                        })
                        speed_records = pd.concat([speed_records, new_record], ignore_index=True)
                        track['recorded'] = True
                        print(f"[Track {tid}] (Forzado) Velocidad: {speed_kmh:.1f} km/h a las {timestamp} | Tipo: {vehicle_type}")
            tracks_to_delete.append(tid)
    for tid in tracks_to_delete:
        if tid in object_tracks:
            del object_tracks[tid]

    # Dibujar los bounding boxes y la velocidad en el frame
    for tid, track in object_tracks.items():
        bbox = track.get('bbox')
        if bbox is not None:
            x1, y1, x2, y2 = bbox
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            if track.get('frozen_speed') is not None:
                cv2.putText(frame, f'{track["frozen_speed"]:.1f} km/h', (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    cv2.imshow('Medición de velocidad', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Guardar el CSV con los registros
speed_records.to_csv(output_csv_path, index=False)
print(f"Registros guardados en: {output_csv_path}")
cap.release()
cv2.destroyAllWindows()
