import pygame as pg
import sys

from settings import *
from map import *
from player import *
from raycasting import *
class Game:
     def __init__(self):
          pg.init()
          pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
          pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
          pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                      pg.GL_CONTEXT_PROFILE_CORE)
          self.screen = pg.display.set_mode((RES), pg.OPENGL|pg.DOUBLEBUF)
          self.clock = pg.time.Clock()
          
          self.novo_game()
          
     def novo_game(self):
          self.map = Map(self)
          self.player = Player(self)
          self.raycasting = RayCasting(self)
          
     def update(self):
          self.player.update()
          self.raycasting.update()
          pg.display.flip()
          self.delta_time = self.clock.tick(FPS)
          pg.display.set_caption(f'{self.clock.get_fps() :.1f}')
     
     def check_events(self):
          """
          Como por enquanto só temos um evento (sair da aplicação),
          essa serve para sair do jogo.
          """
          for event in pg.event.get():
               if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    self.raycasting.destroy()
                    pg.quit()
                    sys.exit()
     
     def run(self):
          while True:
               self.check_events()
               self.update()

if __name__ == '__main__':
     game = Game()
     game.run()
