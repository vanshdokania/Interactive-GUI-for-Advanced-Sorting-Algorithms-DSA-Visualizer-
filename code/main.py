import pygame
import random
import sys
import time


# Constants
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 800
ARRAY_SIZE = 70
RECT_WIDTH = 20
BUTTON_WIDTH, BUTTON_HEIGHT = 150, 50


# Tracking variables
passes = 0
comparisons = 0
swaps = 0
start_time = 0
current_algorithm = ""
time_complexity = ""


# Main colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
PURPLE = (154, 76, 253)
GREY = (205, 205, 205)
BLUE = (76, 226, 253)
DARK_BLUE = (17, 64, 255)
RED = (255, 0, 0)
PINK = (213, 0, 255)
CYAN = (0, 155, 255)
YELLOW = (251, 255, 0)
STEEL = (70, 130, 180)


# Final Colors
DARK_BG = (18, 18, 18)          # Main background
PANEL_BG = (30, 30, 30)         # Left panel (buttons)
ARRAY_BG = (10, 10, 20)         # Array visualization area
HEADING_BG = (25, 25, 35)        # Header background
BAR_OUTLINE = (30, 30, 30)      # Bar outline


# Buttons Colors
BUTTON_IDLE = (50, 50, 60)      # Default state
BUTTON_HOVER = (70, 70, 80)     # Mouse-hover
BUTTON_TEXT = (220, 220, 220)   # Button text


# Special buttons
RESET_BUTTON = (100, 200, 100)  # Green reset
QUIT_BUTTON = (200, 80, 80)     # Red quit


# Sorting bars
BAR_DEFAULT = (180, 180, 180)   # Unsorted
BAR_COMPARE = (255, 255, 0)     # Yellow (comparing)
BAR_SWAP = (255, 50, 50)        # Red (swapping)
BAR_SORTED = (0, 200, 100)      # Green (sorted)
BAR_PIVOT = (200, 0, 200)       # Purple (pivot)
BAR_SELECTED = (0, 150, 255)    # Blue (selected element)


# Header
HEADING_TEXT_COLOR = (0, 200, 200)  # Cyan header text color


# Initialize
arr = []
original_arr = []
complete = False
current_sort = None
paused = False
sorting_speed = 60  # Frames per second


# Setup PyGame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sorting Visualizer")
clock = pygame.time.Clock()


# Button 1 for all sorting options
def draw_buttons_type_1(screen, rect, text, is_hovered=False):
    color = BUTTON_HOVER if is_hovered else BUTTON_IDLE
    pygame.draw.rect(screen, color, rect, border_radius=3)
    font = pygame.font.SysFont(None, 30)
    text_surface = font.render(text, True, BUTTON_TEXT)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)


# Button 2 for QUIT
def draw_buttons_type_2(screen, rect, text, is_hovered=False):
    color = QUIT_BUTTON if "QUIT" in text else RESET_BUTTON
    if is_hovered:
        color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
    pygame.draw.rect(screen, color, rect, border_radius=3)
    font = pygame.font.SysFont(None, 30)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)



# Draw status panel
def draw_stats_panel():


    # Status panel making
    stats_panel = pygame.Rect(SCREEN_WIDTH - 300, 10, 280, 220)  # Creates a surface of status panel
    pygame.draw.rect(screen, PANEL_BG, stats_panel, border_radius=5) # Draws the status panel on the surface
    pygame.draw.rect(screen, (100, 100, 100), stats_panel, 2, border_radius=5) # Draws the border of the status panel
    

    # Font style
    font_small = pygame.font.SysFont("Arial", 18) # Small arial font 
    font_medium = pygame.font.SysFont("Arial", 22, bold=True) # Medium arial bold font # Algorithm's text , Algorithm's name
    

    # Algorithms information
    algo_text = font_medium.render(f"Algorithm:", True, WHITE) # Algorithm's text
    screen.blit(algo_text, (SCREEN_WIDTH - 290, 20)) # Display algo text above the status panel
    algo_name = font_medium.render(current_algorithm, True, YELLOW) # Algorithm's name
    screen.blit(algo_name, (SCREEN_WIDTH - 290, 45)) # Display algo name above the status panel
    

    # Time complexity
    time_comp_text = font_small.render("Time Complexity:", True, WHITE) # Time complexity text
    screen.blit(time_comp_text, (SCREEN_WIDTH - 290, 75)) # Display time complexity above the status panel
    complexity_text = font_small.render(time_complexity, True, CYAN) # Exact time complexity
    screen.blit(complexity_text, (SCREEN_WIDTH - 290, 95))  # Display it above the status panel
    

    # Passes , Comparisons and swaps 
    passes_text = font_small.render(f"Passes: {passes}", True, WHITE)
    comparisons_text = font_small.render(f"Comparisons: {comparisons}", True, WHITE)
    swaps_text = font_small.render(f"Swaps: {swaps}", True, WHITE)
    screen.blit(passes_text, (SCREEN_WIDTH - 290, 120))
    screen.blit(comparisons_text, (SCREEN_WIDTH - 290, 140))
    screen.blit(swaps_text, (SCREEN_WIDTH - 290, 160))
    
    
    # Elapsed time
    if start_time > 0:
        elapsed = time.time() - start_time
        time_text = font_small.render(f"Time: {elapsed:.2f}s", True, YELLOW)
        screen.blit(time_text, (SCREEN_WIDTH - 290, 180))
    
    # Status
    status = "Paused" if paused else "Running" if current_sort else "Idle"
    status_color = YELLOW if paused else GREEN if current_sort else RED
    status_text = font_small.render(f"Status: {status}", True, status_color)
    screen.blit(status_text, (SCREEN_WIDTH - 290, 200))




def reset_stats(): # Reset the stats after every operation selected (executed)
    global passes, comparisons, swaps, start_time
    passes = 0
    comparisons = 0
    swaps = 0
    start_time = time.time()


# Draw the array graph
def draw_array(x=-1, y=-1, z=-1, w=-1):

    # Clear array area only
    array_area = pygame.Rect(200, 80, SCREEN_WIDTH - 220, SCREEN_HEIGHT - 100)
    pygame.draw.rect(screen, ARRAY_BG, array_area)
    
    # Calculate bar dimensions
    bar_width = (SCREEN_WIDTH - 240) // ARRAY_SIZE
    max_bar_height = SCREEN_HEIGHT - 170
    
    for i in range(ARRAY_SIZE):
        bar_height = int((arr[i] / (SCREEN_HEIGHT - 10)) * max_bar_height)
        x_pos = 210 + i * (bar_width + 1)  # +1 for gap between bars
        y_pos = SCREEN_HEIGHT - 90 - bar_height
        
        # Determine bar color
        if complete:
            color = BAR_SORTED
        elif i == z:  # Pivot (QuickSort)
            color = BAR_PIVOT
        elif i == x or i == y:  # Comparing/swapping
            color = BAR_COMPARE
        elif i == w:  # Selected element
            color = BAR_SELECTED
        elif arr[x] > arr[y] and (i == x or i == y):  # Need to swap
            color = BAR_SWAP
        else:
            color = BAR_DEFAULT
        
        # Draw the bar with outline
        pygame.draw.rect(screen, color, (x_pos, y_pos, bar_width, bar_height))
        pygame.draw.rect(screen, BAR_OUTLINE, (x_pos, y_pos, bar_width, bar_height), 1)


# Function of reset array option
def reset_array():
    global arr, original_arr, complete, current_sort
    arr = [random.randint(10, SCREEN_HEIGHT - 100) for _ in range(ARRAY_SIZE)]
    original_arr = arr[:]
    complete = False
    current_sort = None
    reset_stats()


# Selection Sort generator
def selection_sort_gen():
    global current_algorithm, time_complexity
    global complete, passes, comparisons, swaps
    reset_stats()
    current_algorithm = "Selection Sort"
    time_complexity = "O(n²)"
    
    passes = 0

    for i in range(len(arr) - 1):
        passes += 1
        min_idx = i
        for j in range(i + 1, len(arr)):
            comparisons += 1
            if arr[j] < arr[min_idx]:
                min_idx = j
            draw_array(i, min_idx, -1, j)
            yield
        if min_idx != i:
            swaps += 1
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            draw_array(i, min_idx)
            yield
    complete = True


# Insertion Sort generator
def insertion_sort_gen():
    global current_algorithm, time_complexity
    global complete, passes, comparisons, swaps
    reset_stats()
    current_algorithm = "Insertion Sort"
    time_complexity = "O(n²)"
    
    passes = 0

    for i in range(1, len(arr)):
        passes += 1
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            comparisons += 1
            arr[j + 1] = arr[j]
            swaps += 1
            draw_array(i, j + 1)
            yield
            j -= 1
        comparisons += 1 
        arr[j + 1] = key
        draw_array(i, j + 1)
        yield
    complete = True


# Bubble sort generator
def bubble_sort_gen():
    global current_algorithm, time_complexity
    global complete, passes, comparisons, swaps
    reset_stats()
    current_algorithm = "Bubble Sort"
    time_complexity = "O(n²)"
    
    passes = 0
    n = len(arr)
    for i in range(n):
        passes += 1
        swapped = False
        for j in range(n - i - 1):
            comparisons += 1
            if arr[j] > arr[j + 1]:
                swaps += 1
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
                draw_array(j, j + 1)
                yield
            else:
                draw_array(j, j + 1)
                yield
        if not swapped:
            break
    complete = True


# Merge Sort generator
def merge_sort_gen(start, end):
    global complete, comparisons, swaps, passes
    global current_algorithm, time_complexity
    
    reset_stats()
    current_algorithm = "Merge Sort"
    time_complexity = "O(n log n)"
    
    passes = 0
    stack = [(start, end, False)]
    
    while stack:
        start, end, processed = stack.pop()
        
        if start >= end:
            continue
            
        if not processed:
            passes += 1
            mid = (start + end) // 2
            stack.append((start, end, True))
            stack.append((mid + 1, end, False))
            stack.append((start, mid, False))
            yield
        else:
            mid = (start + end) // 2
            yield from merge(start, mid, end)
            yield
    complete = True


# Helper of merge sort
def merge(start, mid, end):
    global complete, comparisons, swaps
    global current_algorithm, time_complexity
    # passes += 1 
    # reset_stats()
    # current_algorithm = "Merge Sort"
    # time_complexity = "O(n log n)"
    left = arr[start:mid + 1]
    right = arr[mid + 1:end + 1]
    i = j = 0
    k = start
    while i < len(left) and j < len(right):
        comparisons += 1
        if left[i] <= right[j]:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
            swaps += 1
        k += 1
        draw_array(k - 1)
        yield
    while i < len(left):
        arr[k] = left[i]
        i += 1
        k += 1
        draw_array(k - 1)
        yield
    while j < len(right):
        arr[k] = right[j]
        j += 1
        k += 1
        draw_array(k - 1)
        yield


# Quick sort generator
def quick_sort_gen(start, end):
    global current_algorithm, time_complexity
    global complete, passes
    reset_stats()
    current_algorithm = "Quick Sort"
    time_complexity = "O(n log n)"
    
    passes = 0
    stack = [(start, end)]
    
    while stack:
        start, end = stack.pop()
        
        if start >= end:
            continue
            
        passes += 1
        pivot = yield from partition(start, end)
        

        if pivot - start > end - pivot:
            stack.append((start, pivot - 1))
            stack.append((pivot + 1, end))
        else:
            stack.append((pivot + 1, end))
            stack.append((start, pivot - 1))
        
        yield
    
    complete = True


# Helper function of quick sort
def partition(start, end):
    global comparisons, swaps
    pivot = arr[start]
    count = 0
    

    for i in range(start + 1, end + 1):
        comparisons += 1
        if arr[i] <= pivot:
            count += 1
    
    pivot_idx = start + count
    if pivot_idx != start:
        swaps += 1
        arr[start], arr[pivot_idx] = arr[pivot_idx], arr[start]
        draw_array(pivot_idx, start)
        yield

  
    i, j = start, end
    while i < pivot_idx and j > pivot_idx:
        comparisons += 1
        if arr[i] <= pivot:
            i += 1
        elif arr[j] > pivot:
            j -= 1
        else:
            swaps += 1
            arr[i], arr[j] = arr[j], arr[i]
            draw_array(i, j)
            yield
            i += 1
            j -= 1
    
    return pivot_idx


# Heapify
def heapify_gen(n, i):
    global comparisons, swaps
    global current_algorithm, time_complexity

    largest = i
    l = 2 * i + 1
    r = 2 * i + 2
    if l < n:
        comparisons += 1
        if arr[l] > arr[largest]:
            largest = l
    if r < n:
        comparisons += 1
        if arr[r] > arr[largest]:
            largest = r
    if largest != i:
        swaps += 1
        arr[i], arr[largest] = arr[largest], arr[i]
        draw_array(i, largest)
        yield
        yield from heapify_gen(n, largest)


# Heap sort generator
def heap_sort_gen():
    global complete, passes, comparisons, swaps
    global current_algorithm, time_complexity
    reset_stats()
    current_algorithm = "Heap Sort"
    time_complexity = "O(n log n)"
    
    passes = 0
    n = len(arr)
    
    # Build heap
    for i in range(n // 2 - 1, -1, -1):
        passes += 1
        yield from heapify_gen(n, i)
        yield
    
    # Extract elements
    for i in range(n - 1, 0, -1):
        passes += 1
        swaps += 1
        arr[i], arr[0] = arr[0], arr[i]
        draw_array(i, 0)
        yield
        yield from heapify_gen(i, 0)
        yield
    complete = True



def main():
    global arr, complete, current_sort, current_algorithm, time_complexity, paused, sorting_speed

    reset_array()

    # Buttons
    reset_button_rect = pygame.Rect(20, 100, BUTTON_WIDTH, BUTTON_HEIGHT)
    selection_sort_button_rect = pygame.Rect(20, 180, BUTTON_WIDTH, BUTTON_HEIGHT)
    insertion_sort_button_rect = pygame.Rect(20, 260, BUTTON_WIDTH, BUTTON_HEIGHT)
    bubble_sort_button_rect = pygame.Rect(20, 340, BUTTON_WIDTH, BUTTON_HEIGHT)
    merge_sort_button_rect = pygame.Rect(20, 420, BUTTON_WIDTH, BUTTON_HEIGHT)
    quick_sort_button_rect = pygame.Rect(20, 500, BUTTON_WIDTH, BUTTON_HEIGHT)
    heap_sort_button_rect = pygame.Rect(20, 580, BUTTON_WIDTH, BUTTON_HEIGHT)
    pause_button_rect = pygame.Rect(20, 660, BUTTON_WIDTH, BUTTON_HEIGHT)
    quit_button_rect = pygame.Rect(20, 740, BUTTON_WIDTH, BUTTON_HEIGHT)

    running = True

    while running:

        screen.fill(DARK_BG)

        # Draw left panel
        pygame.draw.rect(screen, PANEL_BG, (0, 0, 200, SCREEN_HEIGHT))

        # Draw heading
        pygame.draw.rect(screen, HEADING_BG, (200, 0, SCREEN_WIDTH - 200, 80))
        font = pygame.font.SysFont(None, 80)
        heading_text = font.render("Sorting Visualizer", True, HEADING_TEXT_COLOR)
        heading_x = SCREEN_WIDTH // 2
        heading_rect = heading_text.get_rect(center=(heading_x, 40))
        screen.blit(heading_text, heading_rect)

        # Draw array
        draw_array()

        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw buttons with hover effects
        draw_buttons_type_1(screen, reset_button_rect, "Reset Array", reset_button_rect.collidepoint(mouse_pos))
        draw_buttons_type_1(screen, selection_sort_button_rect, "Selection Sort", selection_sort_button_rect.collidepoint(mouse_pos))
        draw_buttons_type_1(screen, insertion_sort_button_rect, "Insertion Sort", insertion_sort_button_rect.collidepoint(mouse_pos))
        draw_buttons_type_1(screen, bubble_sort_button_rect, "Bubble Sort", bubble_sort_button_rect.collidepoint(mouse_pos))
        draw_buttons_type_1(screen, merge_sort_button_rect, "Merge Sort", merge_sort_button_rect.collidepoint(mouse_pos))
        draw_buttons_type_1(screen, quick_sort_button_rect, "Quick Sort", quick_sort_button_rect.collidepoint(mouse_pos))
        draw_buttons_type_1(screen, heap_sort_button_rect, "Heap Sort", heap_sort_button_rect.collidepoint(mouse_pos))
        draw_buttons_type_2(screen, pause_button_rect, "PAUSE" if not paused else "RESUME", pause_button_rect.collidepoint(mouse_pos))
        draw_buttons_type_2(screen, quit_button_rect, "QUIT", quit_button_rect.collidepoint(mouse_pos))

        draw_stats_panel()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if reset_button_rect.collidepoint(event.pos):
                    reset_array()
                    current_sort = None
                    paused = False
                elif selection_sort_button_rect.collidepoint(event.pos):
                    arr = original_arr[:]
                    complete = False
                    current_sort = selection_sort_gen()
                    paused = False
                elif insertion_sort_button_rect.collidepoint(event.pos):
                    arr = original_arr[:]
                    complete = False
                    current_sort = insertion_sort_gen()
                    paused = False
                elif bubble_sort_button_rect.collidepoint(event.pos):
                    arr = original_arr[:]
                    complete = False
                    current_sort = bubble_sort_gen()
                    paused = False
                elif merge_sort_button_rect.collidepoint(event.pos):
                    arr = original_arr[:]
                    complete = False
                    current_sort = merge_sort_gen(0, len(arr) - 1)
                    paused = False
                elif quick_sort_button_rect.collidepoint(event.pos):
                    arr = original_arr[:]
                    complete = False
                    current_sort = quick_sort_gen(0, len(arr) - 1)
                    paused = False
                elif heap_sort_button_rect.collidepoint(event.pos):
                    arr = original_arr[:]
                    complete = False
                    current_sort = heap_sort_gen()
                    paused = False
                elif pause_button_rect.collidepoint(event.pos):
                    if current_sort:  # Only allow pausing if a sort is active
                        paused = not paused
                elif quit_button_rect.collidepoint(event.pos):
                    running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and current_sort:
                    paused = not paused
                elif event.key == pygame.K_UP and sorting_speed < 120:
                    sorting_speed += 10
                elif event.key == pygame.K_DOWN and sorting_speed > 10:
                    sorting_speed -= 10

        # Run sorting step if active and not paused
        if current_sort and not paused:
            try:
                next(current_sort)
            except StopIteration:
                current_sort = None

        pygame.display.flip()
        clock.tick(sorting_speed)

    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    main()