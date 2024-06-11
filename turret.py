import pygame as pg
import math
import constants as c
from turret_data import TURRET_DATA

class Turret(pg.sprite.Sprite):
  def __init__(self, sprite_sheets, tile_x, tile_y, shot_fx):
    pg.sprite.Sprite.__init__(self)
    self.upgrade_level = 1
    self.damage = TURRET_DATA[self.upgrade_level - 1].get("damage")
    self.range = TURRET_DATA[self.upgrade_level - 1].get("range")
    self.cooldown = TURRET_DATA[self.upgrade_level - 1].get("cooldown")
    self.last_shot = pg.time.get_ticks()
    self.selected = False
    self.target = None

    #position variables
    self.tile_x = tile_x
    self.tile_y = tile_y
    #calculate center coordinates
    self.x = (self.tile_x + 0.5) * c.TILE_SIZE
    self.y = (self.tile_y + 0.5) * c.TILE_SIZE
    #shot sound effect
    self.shot_fx = shot_fx

    #animation variables
    self.sprite_sheets = sprite_sheets
    self.animation_list = self.load_images(self.sprite_sheets[self.upgrade_level - 1])
    self.frame_index = 0
    self.update_time = pg.time.get_ticks()

    #update image
    self.angle = 90
    self.original_image = self.animation_list[self.frame_index]
    self.image = pg.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = (self.x, self.y)

    #hiển thị tầm bắn
    self.range_image = pg.Surface((self.range * 2, self.range * 2))
    self.range_image.fill((0, 0, 0))
    self.range_image.set_colorkey((0, 0, 0))
    pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
    self.range_image.set_alpha(100)
    self.range_rect = self.range_image.get_rect()
    self.range_rect.center = self.rect.center

  def load_images(self, sprite_sheet):
    #extract images
    size = sprite_sheet.get_height()
    animation_list = []
    for x in range(c.ANIMATION_STEPS):
      temp_img = sprite_sheet.subsurface(x * size, 0, size, size)
      animation_list.append(temp_img)
    return animation_list

  def update(self, enemy_group, world):
    #nếu đã chọn kẻ địch, bắn
    if self.target:
      self.play_animation()
    else:
      #tìm enemy mới
      if pg.time.get_ticks() - self.last_shot > (self.cooldown / world.game_speed):
        self.pick_target(enemy_group)

  def pick_target(self, enemy_group):
    #tìm kẻ địch
    x_dist = 0
    y_dist = 0
    #kiểm tra enemies có trong tầm bắn
    for enemy in enemy_group:
      if enemy.health > 0:
        x_dist = enemy.pos[0] - self.x
        y_dist = enemy.pos[1] - self.y
        dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
        if dist < self.range:
          self.target = enemy
          self.angle = math.degrees(math.atan2(-y_dist, x_dist))
          #damage
          self.target.health -= self.damage
          if self.upgrade_level==2:
            self.target.damageramp+=1
            self.target.health-=self.target.damageramp
          #gây hiệu ứng làm chậm nếu turret là cấp 3
          if self.upgrade_level==3:
            self.target.slowdowntimer=120
          #gây sát thương lan nếu turret cấp 4, exra là bán kính sát thương nổ
          if self.upgrade_level==4:
            for enemy in enemy_group:
              if enemy.health >0:
                x_exra= enemy.pos[0] - self.target.pos[0]
                y_exra= enemy.pos[1] - self.target.pos[1]
                exra=math.sqrt(x_exra ** 2 + y_exra ** 2)
                if exra < 48:
                  enemy.health -= self.damage
          #gây sát thương cho toanf bộ kẻ địch trong tầm nếu turret cấp 5
          if self.upgrade_level==5:
            for enemy in enemy_group:
              if enemy.health >0:
                x_zap= enemy.pos[0] - self.x
                y_zap= enemy.pos[1] - self.y
                zap=math.sqrt(x_zap ** 2 + y_zap ** 2)
                if zap < self.range:
                  enemy.health -= self.damage//2               
          #play sfx
          self.shot_fx.play()
          break

  def play_animation(self):
    #update image
    self.original_image = self.animation_list[self.frame_index]
    #kiểm tra nếu đã đủ thời gian animation delay trôi qua
    if pg.time.get_ticks() - self.update_time > c.ANIMATION_DELAY:
      self.update_time = pg.time.get_ticks()
      self.frame_index += 1
      #kiểm tra nếu hoạt ảnh đã chạy xong
      if self.frame_index >= len(self.animation_list):
        self.frame_index = 0
        self.last_shot = pg.time.get_ticks()
        self.target = None

  def upgrade(self):
    if self.upgrade_level==5:
      self.upgrade_level=1
    else:
      self.upgrade_level += 1
    self.range = TURRET_DATA[self.upgrade_level - 1].get("range")
    self.cooldown = TURRET_DATA[self.upgrade_level - 1].get("cooldown")
    self.damage = TURRET_DATA[self.upgrade_level - 1].get("damage")
    #thay đổi hình dạng turret khi nâng cấp
    self.animation_list = self.load_images(self.sprite_sheets[self.upgrade_level - 1])
    self.original_image = self.animation_list[self.frame_index]

    #nâng tầm bắn
    self.range_image = pg.Surface((self.range * 2, self.range * 2))
    self.range_image.fill((0, 0, 0))
    self.range_image.set_colorkey((0, 0, 0))
    pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
    self.range_image.set_alpha(100)
    self.range_rect = self.range_image.get_rect()
    self.range_rect.center = self.rect.center

  def draw(self, surface):
    self.image = pg.transform.rotate(self.original_image, self.angle - 90)
    self.rect = self.image.get_rect()
    self.rect.center = (self.x, self.y)
    surface.blit(self.image, self.rect)
    if self.selected:
      surface.blit(self.range_image, self.range_rect)