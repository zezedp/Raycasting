from settings import *
import pygame as pg
import math
import numpy as np

class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.y = PLAYER_POS
        self.dirX, self.dirY = PLAYER_DIR
        self.planoX, self.planoY = PLANO
    def rot(self, A):
        """
        Matriz de Rotação Anti-horária de A graus ou radianos em R2.
        """
        return np.matrix(([math.cos(A), -math.sin(A)],
                          [math.sin(A), math.cos(A)]))
    
    def movement(self):
        """
        Responsável por movimentar o jogador no cenário.
        """
        dx = dy = 0
        keys = pg.key.get_pressed()
        dirX, dirY = PLAYER_DIR
        vec_dir = np.array(([dirX], [dirY]))
        plane = np.array(([self.planoX], [self.planoY]))
        
        if keys[pg.K_w]:
            w = vec_dir * PLAYER_SPEED
            dx += float(w[0])
            dy += float(w[1])
        if keys[pg.K_s]:
            s = self.rot(np.pi) * vec_dir * PLAYER_SPEED
            dx += float(s[0])
            dy += float(s[1])
        if keys[pg.K_a]:
            a = self.rot(-np.pi/2) * vec_dir * PLAYER_SPEED
            dx += float(a[0])
            dy += float(a[1])
        if keys[pg.K_d]:
            d = self.rot(np.pi/2) * vec_dir * PLAYER_SPEED
            dx += float(d[0])
            dy += float(d[1])
            
        self.check_wall_collision(dx,dy)
        
    def check_wall(self, x, y):
        """
        Retorna se a coordenada informada é ou não uma parede.
        """
        return (x,y) not in self.game.map.world_map
    
    def check_wall_collision(self, dx, dy):
        """
        Permite movimentação do jogador, desde que não tenha obstáculos no caminho.
        """
        if self.check_wall(int(self.x + dx), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy)):
            self.y += dy
        
    def update(self):
        self.movement()
    
    @property
    def pos(self):
        """
        Por praticidade, a propriedade 'pos' retorna a posição em coordenadas do jogador.
        """
        return self.x, self.y
    
    @property
    def map_pos(self):
        """
        Retorna as coordenadas em que bloco do mapa o jogador está.
        """
        return math.floor(self.x), math.floor(self.y)
    