import pygame
import sys
import os
import platform
import random
import math
import gc  # 添加这行
from moviepy.editor import VideoFileClip
import pygame.display

class Scene:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.font = game.font
        self.next_scene = None
        self.last_click_time = 0
        self.click_delay = 200
        self.click_cooldown = 0
        self.click_ready = True
        
    def can_handle_click(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_click_time >= self.click_delay:
            self.last_click_time = current_time
            return True
        return False
    
    def handle_events(self, events):
        pass
    
    def update(self):
        # 在update中重置点击就绪状态
        current_time = pygame.time.get_ticks()
        if current_time > self.click_cooldown:
            self.click_ready = True
    
    def cleanup(self):
        """清理场景特定的资源"""
        if hasattr(self, 'bg_images'):
            self.bg_images = []
        gc.collect()
    def draw(self):
        pass

class TitleScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.title_text = "数字江南·智慧苏州"
        self.subtitle_text = "点击任意键继续..."
        self.show_subtitle = True
        self.subtitle_timer = 0
        
        # 加载封面背景图
        self.bg_image = pygame.image.load("assets/cover.jpg")
        self.bg_image = pygame.transform.scale(self.bg_image, (800, 600))
        
        # 创建半透明遮罩，让文字更清晰
        self.overlay = pygame.Surface((800, 600))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(100)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.can_handle_click():
                    self.next_scene = QuizScene(self.game)
    
    def update(self):
        self.subtitle_timer += 1
        if self.subtitle_timer >= 30:
            self.show_subtitle = not self.show_subtitle
            self.subtitle_timer = 0
    
    def draw(self):
        # 绘制背景图
        self.screen.blit(self.bg_image, (0, 0))
        # 绘制遮罩
        self.screen.blit(self.overlay, (0, 0))
        
        # 使用大号字体绘制标题
        title_surface = self.game.title_font.render(self.title_text, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.screen.get_width()//2, 300))
        self.screen.blit(title_surface, title_rect)
        
        if self.show_subtitle:
            subtitle_surface = self.font.render(self.subtitle_text, True, (200, 200, 200))
            subtitle_rect = subtitle_surface.get_rect(center=(self.screen.get_width()//2, 500))
            self.screen.blit(subtitle_surface, subtitle_rect)

class BaseIntroductionScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        
        # 动画相关属性
        self.animation_speed = 8
        self.image_alpha = 0
        self.image_x = 800
        self.target_image_x = 520
        self.text_alpha = 0
        self.animation_complete = False
        
        # 文字位置相关
        self.text_y = 120
        self.target_text_y = 120
        
        # 添加点击提示相关属性
        self.show_continue = False
        self.continue_text = "点击继续..."
        self.continue_alpha = 128
        
        # 加载背景图片
        self.bg_images = []
        self.load_background_images()
        self.current_bg = self.get_random_background()
        
        # 加载右侧展示图片
        self.image = pygame.image.load("assets/fengjing2.jpg")
        self.image = pygame.transform.scale(self.image, (230, 280))

    def load_background_images(self):
        image_dir = "assets/image"
        for file in os.listdir(image_dir):
            if file.endswith(('.jpg', '.jpeg', '.png')) and file != 'guide.png':
                image_path = os.path.join(image_dir, file)
                image = pygame.image.load(image_path)
                image = pygame.transform.scale(image, (800, 600))
                self.bg_images.append(image)
    
    def get_random_background(self):
        if self.bg_images:
            return random.choice(self.bg_images)
        return None
        
    def update(self):
        # 更新动画状态
        if self.image_x > self.target_image_x:
            self.image_x = max(self.target_image_x, self.image_x - self.animation_speed)
            
        if self.image_alpha < 255:
            self.image_alpha = min(255, self.image_alpha + self.animation_speed)
            
        if self.text_alpha < 255:
            self.text_alpha = min(255, self.text_alpha + self.animation_speed)
        
        # 检查动画是否完成
        if (self.image_x == self.target_image_x and 
            self.image_alpha == 255 and 
            self.text_alpha == 255):
            self.animation_complete = True
            
        # 当动画完成后显示提示
        if self.animation_complete:
            self.show_continue = True
            # 让提示闪烁
            self.continue_alpha = 128 + int(127 * math.sin(pygame.time.get_ticks() / 500))
            
        # 更新点击就绪状态
        super().update()  # 确保调用父类的update方法

    def draw(self):
        # 绘制背景
        if self.current_bg:
            self.screen.blit(self.current_bg, (0, 0))
        
        # 添加半透明遮罩
        overlay = pygame.Surface((800, 600))
        overlay.fill((255, 255, 255))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        # 绘制文本（整段动画）
        y_offset = self.text_y
        for line in self.text:
            if line.strip():  # 跳过空行
                text_surface = self.font.render(line, True, (0, 0, 0))
                text_surface.set_alpha(self.text_alpha)
                text_rect = text_surface.get_rect(left=50, top=y_offset)
                self.screen.blit(text_surface, text_rect)
            y_offset += 35  # 行间距
        
        # 绘制右侧图片
        if self.image:
            temp_surface = self.image.copy()
            temp_surface.set_alpha(self.image_alpha)
            self.screen.blit(temp_surface, (self.image_x, 160))
        # 绘制继续提示
        if self.show_continue and self.animation_complete:
            continue_surface = self.font.render(self.continue_text, True, (0, 0, 0))
            continue_surface.set_alpha(self.continue_alpha)
            continue_rect = continue_surface.get_rect(center=(400, 550))
            self.screen.blit(continue_surface, continue_rect)
            

    def cleanup(self):
        """清理场景特定的资源"""
        if hasattr(self, 'bg_images'):
            self.bg_images = []
        if hasattr(self, 'image'):
            self.image = None
        if hasattr(self, 'current_bg'):
            self.current_bg = None
        gc.collect()
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.can_handle_click() and self.animation_complete:
                    next_scene = self.get_next_scene()
                    if next_scene:
                        self.next_scene = next_scene
                        return
    def get_next_scene(self):
        # 子类需要实现这个方法
        return None
                
class IntroductionScene1(BaseIntroductionScene):
    def __init__(self, game):
        self.text = [
            "拙政园，始建于明正德初年(1509-1516)，",
            "是苏州现存最大的古典园林。",
            "",
            "它以其独特的'一园三区'布局闻名于世，",
            "东区以建筑为主，中区以水景为主，",
            "西区以山景为主，体现了'咫尺之内，",
            "自成天地'的园林特色。",
            "",
            "园内亭台楼阁、山水花木相映成趣，",
            "处处体现'虽由人作，宛自天开'的意境。"
        ]
        super().__init__(game)
        
        # 加载拙政园特定图片
        self.image = pygame.image.load("assets/zhuozhengyuan.jpg")
        self.image = pygame.transform.scale(self.image, (230, 280))
    def get_next_scene(self):
        return QuizScene(self.game)
                
class IntroductionScene2(BaseIntroductionScene):
    def __init__(self, game):
        self.text = [
            "苏州园林的'移步换景'是其最显著的特色，",
            "游客每走几步就能看到不同的景致。",
            "",
            "这种设计理念通过精心布局，将有限的",
            "空间营造出无限的景观变化。",
            "",
            "园中的曲廊、游廊既是观景的途径，",
            "也是景观的一部分，将游览体验和",
            "艺术欣赏完美结合。"
        ]
        super().__init__(game)
    def get_next_scene(self):
        return QuizScene(self.game)

class IntroductionScene3(BaseIntroductionScene):
    def __init__(self, game):
        self.text = [
            "在数字化时代，苏州园林正在经历创新性的转变。",
            "通过科技手段，这些古老的园林焕发新生。",
            "",
            "数字化保护不仅包括3D扫描建档、VR复原，",
            "还包括智能管理系统的应用。",
            "",
            "游客可以通过手机APP获取园林导览，",
            "体验AR增强现实技术带来的互动体验。",
            "",
            "这种传统与现代的结合，让人们能更好地理解和欣赏园林文化。"
        ]
        super().__init__(game)
        self.image = pygame.image.load("assets/vr.jpg")
        self.image = pygame.transform.scale(self.image, (230, 280))

    def get_next_scene(self):
        print("Creating PuzzleScene") # 添加调试输出
        return PuzzleScene(self.game)
                    
class QuizScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        # 删除原来的全局变量检查
        # if not hasattr(QuizScene, 'global_question'):
        #     QuizScene.global_question = 0
        
        # 使用游戏实例的问题序号
        self.current_question = self.game.current_question
        
        
        # 加载导游图片
        self.guide_image = pygame.image.load("assets/guide.png")
        self.guide_image = pygame.transform.scale(self.guide_image, (150, 200))
        
        # 背景图片列表
        self.bg_images = []
        self.load_background_images()
        self.current_bg = self.get_random_background()
        
        # 动画相关的属性
        self.dialog_alpha = 0
        self.options_alpha = [0] * 4
        self.animation_speed = 5
        self.dialog_box_y = -100
        self.target_dialog_y = 150
        self.result_alpha = 0
        self.result_y = 650
        
        self.questions = [
            {
                'text': "苏州最大的园林是哪一座？",
                'options': ["拙政园", "留园", "狮子林", "网师园"],
                'correct': 0,
                'description': "拙政园是苏州最大的古典园林。"
            },
            {
                'text': "苏州园林最著名的造园理念是什么？",
                'options': ["小中见大", "移步换景", "借景抄园", "虚实相生"],
                'correct': 1,
                'description': "移步换景是苏州园林的精髓。"
            },
            {
                'text': "数字技术在苏州园林中的创新应用是？",
                'options': [
                    "VR实景导览", 
                    "电子讲解器", 
                    "环境监测", 
                    "智能灯光"
                ],
                'correct': 0,
                'description': "VR实景导览让游客足不出户也能身临其境。"
            }
        ]
        
        self.selected_option = None
        self.show_result = False
        self.answered_correctly = False
        
        # 创建半透明遮罩
        self.overlay = pygame.Surface((800, 600))
        self.overlay.fill((255, 255, 255))
        self.overlay.set_alpha(180)
        
        # 对话框
        self.dialog_box = pygame.Surface((500, 80))
        self.dialog_box.fill((245, 245, 245))
        pygame.draw.rect(self.dialog_box, (100, 100, 100), self.dialog_box.get_rect(), 2)

    def load_background_images(self):
        image_dir = "assets/image"
        for file in os.listdir(image_dir):
            if file.endswith(('.jpg', '.jpeg', '.png')) and file != 'guide.png':
                image_path = os.path.join(image_dir, file)
                image = pygame.image.load(image_path)
                image = pygame.transform.scale(image, (800, 600))
                self.bg_images.append(image)

    def get_random_background(self):
        if self.bg_images:
            return random.choice(self.bg_images)
        return None

    def update(self):
        if self.dialog_box_y < self.target_dialog_y:
            self.dialog_box_y += (self.target_dialog_y - self.dialog_box_y) * 0.1
        
        if self.dialog_alpha < 255:
            self.dialog_alpha = min(255, self.dialog_alpha + self.animation_speed)
        
        for i in range(4):
            if self.dialog_alpha >= 200:
                self.options_alpha[i] = min(255, self.options_alpha[i] + self.animation_speed)

    def draw(self):
        if self.current_bg:
            self.screen.blit(self.current_bg, (0, 0))
        self.screen.blit(self.overlay, (0, 0))
        
        current_q = self.questions[self.current_question]
        
        self.screen.blit(self.guide_image, (30, 150))
        
        title = self.font.render(f"第 {self.current_question + 1} 题", True, (0, 0, 0))
        self.screen.blit(title, (30, 20))
        
        dialog_surface = self.dialog_box.copy()
        dialog_surface.set_alpha(self.dialog_alpha)
        self.screen.blit(dialog_surface, (200, self.dialog_box_y))
        
        question_surface = self.font.render(current_q['text'], True, (0, 0, 0))
        question_surface.set_alpha(self.dialog_alpha)
        self.screen.blit(question_surface, (220, self.dialog_box_y + 20))
        
        # 绘制选项
        for i, option in enumerate(current_q['options']):
            button_rect = pygame.Rect(200, 250 + i*45, 400, 40)
            
            # 绘制按钮背景
            if self.selected_option == i:
                # 选中状态的背景色
                button_bg = pygame.Surface((400, 40))
                button_bg.fill((220, 220, 220))
                self.screen.blit(button_bg, button_rect)
            
            # 绘制按钮边框
            pygame.draw.rect(self.screen, (100, 100, 100), button_rect, 2)
            
            # 绘制选项文字
            color = (0, 0, 0)
            if self.show_result:
                if i == current_q['correct']:
                    color = (0, 155, 0)  # 正确答案显示绿色
                elif i == self.selected_option and i != current_q['correct']:
                    color = (155, 0, 0)  # 错误选择显示红色
            
            text = self.font.render(f"{chr(65+i)}. {option}", True, color)
            text_rect = text.get_rect(left=220, centery=button_rect.centery)
            self.screen.blit(text, text_rect)
        
        if self.show_result:
            result_bg = pygame.Surface((400, 100))
            result_bg.fill((255, 255, 255))
            result_bg.set_alpha(200)
            self.screen.blit(result_bg, (200, 450))
            
            result_text = "回答正确！" if self.answered_correctly else "回答错误！"
            result_color = (0, 255, 0) if self.answered_correctly else (255, 0, 0)
            result_surface = self.font.render(result_text, True, result_color)
            self.screen.blit(result_surface, (200, 450))
            
            desc = self.font.render(current_q['description'], True, (0, 0, 0))
            self.screen.blit(desc, (200, 480))
            
            next_text = self.font.render("点击继续", True, (0, 0, 0))
            self.screen.blit(next_text, (200, 550))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.can_handle_click():
                    return
                
                mouse_pos = event.pos
                if not self.show_result:
                    # 检查选项点击
                    for i, option in enumerate(self.questions[self.current_question]['options']):
                        option_rect = pygame.Rect(200, 250 + i*45, 400, 40)
                        if option_rect.collidepoint(mouse_pos):
                            self.selected_option = i
                            self.show_result = True
                            self.answered_correctly = (i == self.questions[self.current_question]['correct'])
                            self.dialog_alpha = 255
                            return
                
                elif self.show_result:
                    # 使用游戏实例的问题序号，而不是类变量
                    self.game.current_question += 1
                    
                    # 根据当前问题序号决定下一个场景
                    if self.game.current_question == 1:
                        self.next_scene = IntroductionScene1(self.game)
                    elif self.game.current_question == 2:
                        self.next_scene = IntroductionScene2(self.game)
                    elif self.game.current_question == 3:
                        self.next_scene = IntroductionScene3(self.game)
                    elif self.game.current_question >= len(self.questions):
                        self.next_scene = PuzzleScene(self.game)                

class PuzzleScene(Scene):
    def __init__(self, game):
        print("PuzzleScene initialized")
        super().__init__(game)
        
        # 首先初始化基本变量，避免出现属性未定义的情况
        self.dragging = None
        self.drag_offset = (0, 0)
        self.pieces = []
        self.completed = False
        self.show_complete_message = False
        self.complete_alpha = 0
        self.complete_text = "恭喜完成! 点击继续..."
        
        try:
            self.title_text = "拼图游戏"
            self.instruction_text = "拖动拼图块完成拼图"
            
            # 加载原始图片
            self.original_image = pygame.image.load("assets/fengjing2.jpg")
            
            # 创建参考图像（缩小版）
            self.reference_image = pygame.transform.scale(self.original_image, (300, 300))
            
            # 设置拼图区域
            self.game_area = pygame.Rect(450, 150, 300, 300)
            
            # 计算每个拼图块的大小
            self.grid_size = 100  # 300/3 = 100
            
            # 创建拼图块
            self.create_pieces()
            
        except Exception as e:
            print(f"Error in PuzzleScene initialization: {e}")      
    def create_pieces(self):
        # 确保原始图片已经缩放到正确大小
        self.original_image = pygame.transform.scale(self.original_image, (300, 300))
        
        # 打乱拼图块的初始位置
        positions = [(x, y) for x in range(3) for y in range(3)]
        random.shuffle(positions)
        
        for i, (grid_x, grid_y) in enumerate(positions):
            # 计算原始图片中的裁剪位置
            orig_x = (i % 3) * self.grid_size
            orig_y = (i // 3) * self.grid_size
            
            # 计算目标位置（正确位置）
            target_x = self.game_area.left + (i % 3) * self.grid_size
            target_y = self.game_area.top + (i // 3) * self.grid_size
            
            # 创建拼图块表面并从原图中裁剪对应区域
            piece_surface = pygame.Surface((self.grid_size, self.grid_size))
            piece_rect = pygame.Rect(orig_x, orig_y, self.grid_size, self.grid_size)
            piece_surface.blit(self.original_image, (0, 0), piece_rect)
            
            # 计算初始位置（打乱的位置）
            initial_x = self.game_area.left + grid_x * self.grid_size
            initial_y = self.game_area.top + grid_y * self.grid_size
            
            # 创建拼图块对象
            self.pieces.append({
                'surface': piece_surface,
                'rect': pygame.Rect(initial_x, initial_y, self.grid_size, self.grid_size),
                'target': (target_x, target_y),
                'correct': False,
                'index': i
            })
            print(f"Created piece {i}: target={target_x},{target_y}, initial={initial_x},{initial_y}")
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 检查是否完成拼图并点击继续
                if self.show_complete_message and self.complete_alpha >= 255:
                    if self.can_handle_click():
                        print("Creating VideoScene")
                        self.next_scene = VideoScene(self.game)
                        return
                
                # 拼图拖动逻辑
                mouse_pos = event.pos
                for piece in self.pieces:
                    if piece['rect'].collidepoint(mouse_pos):
                        self.dragging = piece
                        self.drag_offset = (
                            piece['rect'].x - mouse_pos[0],
                            piece['rect'].y - mouse_pos[1]
                        )
                        # 将当前拖拽的块移到最上层
                        self.pieces.remove(piece)
                        self.pieces.append(piece)
                        break
                        
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragging:
                    # 检查是否放在正确位置
                    piece_center = self.dragging['rect'].center
                    target_pos = self.dragging['target']
                    target_center = (
                        target_pos[0] + self.grid_size/2,
                        target_pos[1] + self.grid_size/2
                    )
                    
                    # 改进的吸附判断逻辑
                    distance = math.sqrt(
                        (piece_center[0] - target_center[0])**2 +
                        (piece_center[1] - target_center[1])**2
                    )
                    
                    if distance < 50:  # 吸附距离阈值
                        # 吸附到正确位置
                        self.dragging['rect'].topleft = target_pos
                        self.dragging['correct'] = True
                        print(f"Piece {self.dragging['index']} snapped to position {target_pos}")
                        
                        # 立即检查是否完成拼图
                        if self.check_completion():
                            print("Puzzle completed!")
                            self.show_complete_message = True
                            self.complete_alpha = 0  # 确保从0开始淡入
                    else:
                        self.dragging['correct'] = False
                        print(f"Piece not in correct position. Distance: {distance}")
                    
                    self.dragging = None
                    
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    mouse_pos = event.pos
                    self.dragging['rect'].x = mouse_pos[0] + self.drag_offset[0]
                    self.dragging['rect'].y = mouse_pos[1] + self.drag_offset[1]
                    
    def update(self):
        # 更新完成消息的淡入效果
        if self.show_complete_message and self.complete_alpha < 255:
            self.complete_alpha = min(255, self.complete_alpha + 5)
        
        super().update()
        
    def check_completion(self):
        all_correct = True
        incorrect_pieces = []
        for i, piece in enumerate(self.pieces):
            # 检查位置是否正确
            current_pos = piece['rect'].topleft
            target_pos = piece['target']
            if abs(current_pos[0] - target_pos[0]) > 5 or abs(current_pos[1] - target_pos[1]) > 5:
                all_correct = False
                incorrect_pieces.append(i)
                piece['correct'] = False
            else:
                piece['correct'] = True
        
        if not all_correct:
            print(f"Puzzle not complete. Incorrect pieces: {incorrect_pieces}")
        else:
            print("All pieces in correct position!")
            self.completed = True
        
        return all_correct
        
    def draw(self):
        try:
            # 清空屏幕并设置背景色
            self.screen.fill((240, 240, 240))
            
            # 绘制标题
            title_surface = self.font.render(self.title_text, True, (0, 0, 0))
            self.screen.blit(title_surface, (20, 20))
            
            # 绘制说明
            instruction_surface = self.font.render(self.instruction_text, True, (100, 100, 100))
            self.screen.blit(instruction_surface, (20, 60))
            
            # 绘制参考图像
            self.screen.blit(self.reference_image, (50, 150))
            
            # 绘制拼图区域边框
            pygame.draw.rect(self.screen, (100, 100, 100), self.game_area, 2)
            
            # 绘制拼图块
            for piece in self.pieces:
                self.screen.blit(piece['surface'], piece['rect'])
            
            # 绘制完成消息
            if self.show_complete_message:
                # 创建半透明背景
                overlay = pygame.Surface((800, 100))
                overlay.fill((255, 255, 255))
                overlay.set_alpha(min(200, self.complete_alpha))
                overlay_rect = overlay.get_rect(center=(400, 500))
                self.screen.blit(overlay, overlay_rect)
                
                # 绘制完成消息
                complete_surface = self.font.render(self.complete_text, True, (0, 150, 0))
                complete_surface.set_alpha(self.complete_alpha)
                complete_rect = complete_surface.get_rect(center=(400, 500))
                self.screen.blit(complete_surface, complete_rect)
                
                # 添加点击提示
                if self.complete_alpha >= 255:
                    hint_surface = self.font.render("点击继续...", True, (100, 100, 100))
                    hint_rect = hint_surface.get_rect(center=(400, 540))
                    self.screen.blit(hint_surface, hint_rect)
            
            pygame.display.flip()
            
        except Exception as e:
            print(f"Error in PuzzleScene draw: {e}")
            
    def cleanup(self):
        """清理场景特定的资源"""
        if hasattr(self, 'original_image'):
            self.original_image = None
        if hasattr(self, 'reference_image'):
            self.reference_image = None
        if hasattr(self, 'pieces'):
            self.pieces = []
        gc.collect()
                   
class VideoScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.video_path = "assets/video.mp4"
        
        # 初始化默认属性
        self.is_playing = False
        self.frame_iterator = None
        self.frame_surface = None
        self.video = None
        self.frame_index = 0
        self.current_time = 0
        
        # 初始化标题背景和其他UI元素
        self.title_bg = pygame.Surface((800, 80))
        self.title_bg.fill((0, 0, 0))
        self.title_bg.set_alpha(200)
        
        try:
            print(f"尝试加载视频: {self.video_path}")
            if not os.path.exists(self.video_path):
                print(f"错误：视频文件不存在: {self.video_path}")
                raise FileNotFoundError(f"视频文件不存在: {self.video_path}")
            
            # 处理 PIL.Image 版本兼容性
            from PIL import Image
            if hasattr(Image, 'Resampling'):
                resize_method = Image.Resampling.LANCZOS
            else:
                resize_method = Image.LANCZOS
            
            print("开始加载VideoFileClip...")
            self.video = VideoFileClip(self.video_path, audio=False)
            print("VideoFileClip加载成功")
            
            self.title_text = "数字园林简介"
            self.subtitle_text = "探索传统与科技的完美融合"
            
            self.video_size = (700, 394)
            self.video_pos = ((800 - self.video_size[0]) // 2, 100)
            
            # 使用新的缩放方法
            def resize_with_lanczos(clip, newsize):
                from PIL import Image
                import numpy as np
                
                def resize_frame(frame):
                    img = Image.fromarray(frame)
                    img = img.resize(newsize, resize_method)
                    return np.array(img)
                
                return clip.fl_image(resize_frame)
            
            # 应用新的缩放方法
            self.video = resize_with_lanczos(self.video, self.video_size)
            self.frame_iterator = self.video.iter_frames()
            
            # 设置播放控制
            self.is_playing = True
            self.frame_index = 0
            self.current_time = 0
            self.duration = self.video.duration * 1000
            self.total_frames = int(self.video.duration * self.video.fps)
            
            # 进度条设置
            self.progress_rect = pygame.Rect(50, 520, 700, 10)
            self.progress_handle_radius = 8
            
            # 提示文本
            self.skip_text = "点击跳过 >>"
            self.skip_alpha = 128
            
            # 帧率控制
            self.target_fps = self.video.fps
            self.frame_time = 1.0 / self.target_fps
            self.accumulated_time = 0
            self.last_frame_time = pygame.time.get_ticks() / 1000.0
            
            print("视频初始化完成")
            
        except Exception as e:
            print(f"视频加载错误: {str(e)}")
            print(f"错误类型: {type(e).__name__}")
            import traceback
            print("详细错误信息:")
            traceback.print_exc()
            # 如果视频加载失败，跳转到感谢场景
            self.next_scene = ThankScene(game)
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.can_handle_click():
                    return
                    
                mouse_pos = event.pos
                
                # 检查跳过按钮点击
                skip_rect = pygame.Rect(650, 530, 130, 50)
                if skip_rect.collidepoint(mouse_pos):
                    self.cleanup()
                    self.next_scene = ThankScene(self.game)
                    return
                
                # 进度条点击不需要延迟
                if abs(mouse_pos[1] - self.progress_rect.centery) < 10:
                    if self.progress_rect.left <= mouse_pos[0] <= self.progress_rect.right:
                        self.handle_progress_click(mouse_pos[0])
    def handle_progress_click(self, x_pos):
        """处理进度条点击"""
        try:
            # 计算新的进度
            progress = (x_pos - self.progress_rect.left) / self.progress_rect.width
            self.frame_index = int(progress * self.total_frames)
            
            # 重新加载视频
            start_time = self.frame_index / self.video.fps
            self.video.close()  # 先关闭当前视频
            self.video = VideoFileClip(self.video_path, audio=False)
            self.video = self.video.resize(self.video_size)
            self.video = self.video.subclip(start_time)
            self.frame_iterator = self.video.iter_frames()
            self.current_time = start_time * 1000
            self.accumulated_time = 0
            self.last_frame_time = pygame.time.get_ticks() / 1000.0
        except Exception as e:
            print(f"视频进度调整错误: {e}")
            
    def update(self):
        if not hasattr(self, 'video') or not self.video:
            return
            
        if self.is_playing and hasattr(self, 'frame_iterator') and self.frame_iterator:
            current_time = pygame.time.get_ticks() / 1000.0
            delta_time = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            self.accumulated_time += delta_time
            
            while self.accumulated_time >= self.frame_time:
                try:
                    frame = next(self.frame_iterator)
                    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                    self.frame_surface = frame_surface
                    self.frame_index += 1
                    self.current_time = (self.frame_index / self.video.fps) * 1000
                    self.accumulated_time -= self.frame_time
                except StopIteration:
                    self.is_playing = False
                    self.cleanup()
                    self.next_scene = ThankScene(self.game)
                    break
            
            # 闪烁跳过提示
            self.skip_alpha = 128 + int(127 * math.sin(pygame.time.get_ticks() / 500))
    def draw(self):
        if not hasattr(self, 'video') or not self.video:
            return
            
        # 填充黑色背景
        self.screen.fill((0, 0, 0))
        
        # 绘制视频帧
        if self.frame_surface:
            self.screen.blit(self.frame_surface, self.video_pos)
        
        # 绘制标题背景和标题
        self.screen.blit(self.title_bg, (0, 0))
        title_surface = self.font.render(self.title_text, True, (255, 255, 255))
        subtitle_surface = self.font.render(self.subtitle_text, True, (200, 200, 200))
        self.screen.blit(title_surface, (20, 20))
        self.screen.blit(subtitle_surface, (20, 50))
        
        # 绘制进度条
        pygame.draw.rect(self.screen, (100, 100, 100), self.progress_rect)
        if self.duration > 0:
            progress = self.current_time / self.duration
            progress_width = int(self.progress_rect.width * progress)
            pygame.draw.rect(self.screen, (255, 255, 255),
                           (self.progress_rect.left, self.progress_rect.top,
                            progress_width, self.progress_rect.height))
        
        # 绘制跳过提示
        skip_surface = self.font.render(self.skip_text, True, (255, 255, 255))
        skip_surface.set_alpha(self.skip_alpha)
        self.screen.blit(skip_surface, (700, 550))
    def cleanup(self):
        """清理视频资源"""
        if hasattr(self, 'video') and self.video:
            try:
                self.video.close()
            except:
                pass
            self.video = None
        
        self.frame_iterator = None
        self.frame_surface = None

# 重新设计 ThankScene
class ThankScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.title_text = "感谢观看"
        self.messages = [
            "感谢您观看数字园林",
            "让我们一起探索传统与科技的完美融合",
            "开启智慧园林新时代"
        ]
        self.show_continue = True
        self.continue_text = "点击任意处结束程序"
        self.alpha = 0
        self.fade_speed = 3
        
        # 优雅的背景色
        self.bg = pygame.Surface((800, 600))
        self.bg.fill((245, 245, 240))  # 淡米色背景
        
        # 添加柔和的渐变效果
        self.gradient = pygame.Surface((800, 600), pygame.SRCALPHA)
        for i in range(600):
            alpha = int(100 * (1 - i/600))  # 减小渐变强度
            pygame.draw.line(self.gradient, (220, 220, 215, alpha), (0, i), (800, i))
    
    def draw(self):
        # 绘制背景
        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.gradient, (0, 0))
        
        # 绘制标题
        title_surface = self.font.render(self.title_text, True, (70, 70, 70))
        title_rect = title_surface.get_rect(center=(400, 150))
        title_surface.set_alpha(self.alpha)
        self.screen.blit(title_surface, title_rect)
        
        # 绘制息
        for i, message in enumerate(self.messages):
            msg_surface = self.font.render(message, True, (100, 100, 100))
            msg_rect = msg_surface.get_rect(center=(400, 250 + i * 50))
            msg_surface.set_alpha(self.alpha)
            self.screen.blit(msg_surface, msg_rect)
        
        # 绘制继续提示（修复这里）
        if self.show_continue and self.alpha >= 255:
            continue_surface = self.font.render(self.continue_text, True, (150, 150, 150))
            continue_rect = continue_surface.get_rect(center=(400, 500))
            self.screen.blit(continue_surface, continue_rect)  # 添加这行
            
            # 添加额外的提示
            hint_surface = self.font.render("程序即将结束...", True, (150, 150, 150))
            hint_rect = hint_surface.get_rect(center=(400, 550))
            self.screen.blit(hint_surface, hint_rect)

    def update(self):
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + self.fade_speed)
        
        # 闪烁继续提示
        if pygame.time.get_ticks() % 1000 < 500:
            self.show_continue = True
        else:
            self.show_continue = False
    

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.alpha >= 255 and self.can_handle_click():
                    pygame.quit()
                    sys.exit()
                
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("数字江南·智慧苏州")
        self.clock = pygame.time.Clock()
        self.font = self.init_font(24)
        self.title_font = self.init_font(48)  # 添加大号字体
        
        # 添加问题序号初始化
        self.current_question = 0
        
        # 加载并播放背景音乐
        self.bg_music = pygame.mixer.Sound("assets/preview.mp3")
        self.bg_music.set_volume(0.3)  # 设置音量为30%
        self.bg_music.play(loops=-1)  # loops=-1表示无限循环
        
        self.current_scene = TitleScene(self)
        # self.current_scene = VideoScene(self)

    def cleanup(self):
        # 停止并释放音乐资源
        self.bg_music.stop()
        pygame.mixer.quit()
        
    def init_font(self, size):
        if platform.system() == "Darwin":
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/STHeiti Light.ttc"
            ]
        else:
            font_paths = [
                "C:\\Windows\\Fonts\\simhei.ttf",
                "C:\\Windows\\Fonts\\msyh.ttc"
            ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                return pygame.font.Font(font_path, size)
        return pygame.font.Font(None, size)
    
    def run(self):
        running = True
        last_scene = None
        
        while running:
            current_time = pygame.time.get_ticks()
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
            
            # 场景切换优化
            if self.current_scene.next_scene:
                print(f"Current scene: {type(self.current_scene).__name__}")
                print(f"Next scene: {type(self.current_scene.next_scene).__name__}")
                if last_scene != self.current_scene.next_scene:
                    # 确保当前场景被清理
                    self.current_scene.cleanup()
                    # 清空屏幕
                    self.screen.fill((255, 255, 255))
                    pygame.display.flip()
                    
                    last_scene = self.current_scene
                    self.current_scene = self.current_scene.next_scene
                    self.current_scene.click_cooldown = current_time + 200
                    print(f"Scene switched to {type(self.current_scene).__name__}")
            
            self.current_scene.handle_events(events)
            self.current_scene.update()
            self.current_scene.draw()
            
            pygame.display.flip()
            self.clock.tick(60)
if __name__ == "__main__":
    game = Game()
    game.run()