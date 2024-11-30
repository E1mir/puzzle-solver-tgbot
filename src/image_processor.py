import cv2
import numpy as np

async def solve_puzzle(input_path, output_path):
    image = cv2.imread(input_path)
    if image is None:
        print(f"Failed to load image: {input_path}")
        return None
    
    height, width, _ = image.shape
    top_offset = int(0.1 * height)
    bottom_offset = int(0.9 * height)
    game_field = image[top_offset:bottom_offset, :]

    gray_game_field = cv2.cvtColor(game_field, cv2.COLOR_BGR2GRAY)
    _, binary_game_field = cv2.threshold(gray_game_field, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(binary_game_field, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cell_positions = []
    start_point = None
    max_brightness = -1
    start_contour_index = -1

    for index, contour in enumerate(contours):
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
        
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            if 20 < w < 100 and 20 < h < 100:
                margin = int(0.25 * min(w, h))
                cell_center = gray_game_field[y+margin:y+h-margin, x+margin:x+w-margin]
                avg_brightness = np.mean(cell_center)

                if avg_brightness > max_brightness:
                    max_brightness = avg_brightness
                    start_point = (x + w // 2, y + h // 2)
                    start_contour_index = len(cell_positions)

                cell_positions.append((x + w // 2, y + h // 2))

    adjacency_list = {i: [] for i in range(len(cell_positions))}
    for i, (x1, y1) in enumerate(cell_positions):
        for j, (x2, y2) in enumerate(cell_positions):
            if i != j:
                if (abs(x1 - x2) <= 10 and abs(y1 - y2) <= 120) or (abs(y1 - y2) <= 10 and abs(x1 - x2) <= 120):
                    adjacency_list[i].append(j)

    start_node_index = start_contour_index
    if start_node_index is not None:
        def dfs(adjacency_list, start_node, cell_positions):
            def dfs_recursive(node, path, visited):
                if len(path) == len(cell_positions):
                    return path

                for neighbor in adjacency_list[node]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        result = dfs_recursive(neighbor, path + [neighbor], visited)
                        if result:
                            return result
                        visited.remove(neighbor)
                return None

            visited = set([start_node])
            return dfs_recursive(start_node, [start_node], visited) or []

        full_path = dfs(adjacency_list, start_node_index, cell_positions)

        if full_path:
            for i in range(len(full_path) - 1):
                pos1 = cell_positions[full_path[i]]
                pos2 = cell_positions[full_path[i + 1]]
                pos1 = (pos1[0], pos1[1] + top_offset)
                pos2 = (pos2[0], pos2[1] + top_offset)
                cv2.line(image, pos1, pos2, (0, 0, 255), 5)
        else:
            print('Path not found')
    else:
        print('Start point not found')

    cv2.imwrite(output_path, image)
    return output_path
