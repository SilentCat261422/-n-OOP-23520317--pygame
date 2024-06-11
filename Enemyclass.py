import pygame
#create an Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        pygame.sprite.Sprite.__init__(self)
        self.image=image
        self.rect=self.image.get_rect()
        self.rect.center=pos

    def move(self):
        self.rect.x += 1