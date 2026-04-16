import cv2


def draw_panel(frame, title, lines):
    panel_width = 420
    panel_height = 40 + (len(lines) * 28)
    overlay = frame.copy()
    cv2.rectangle(overlay, (15, 15), (15 + panel_width, 15 + panel_height), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    cv2.putText(
        frame,
        title,
        (30, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
    )

    y = 78
    for line in lines:
        cv2.putText(
            frame,
            line,
            (30, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (220, 255, 220),
            2,
        )
        y += 28


def draw_status_line(frame, text):
    height, width = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, height - 40), (width, height), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    cv2.putText(
        frame,
        text,
        (20, height - 14),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1,
    )
