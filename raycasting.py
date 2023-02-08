import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from settings import *

class RayCasting:
    def __init__(self, game):
        self.game = game
        
        #configuração padrão do OpenGL
        self.shader = self.createShader("shaders/frameBufferVertex.txt",
                                        "shaders/frameBufferFragment.txt")
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glUseProgram(self.shader)
        
        self.createQuad()
        self.createColorBuffer()

        self.colors = [
                        (0 << 24) + (0 << 16) + (128 << 8) + 255,
                        (0 << 24) + (128 << 16) + (0 << 8) + 255,
                        (0 << 24) + (128 << 16) + (128 << 8) + 255,
                        (128 << 24) + (0 << 16) + (0 << 8) + 255,
                        (128 << 24) + (0 << 16) + (128 << 8) + 255
                    ]
    
    def createQuad(self):
        """
        Cria os vértices para 'quad'
        """
        # x, y, z, s, t
        self.vertices = np.array(
            ( 1.0,  1.0, 0.0, 0.0, 1.0, #top-right
             -1.0,  1.0, 0.0, 0.0, 0.0, #top-left
             -1.0, -1.0, 0.0, 1.0, 0.0, #bottom-left
             -1.0, -1.0, 0.0, 1.0, 0.0, #bottom-left
              1.0, -1.0, 0.0, 1.0, 1.0, #bottom-right
              1.0,  1.0, 0.0, 0.0, 1.0), #top-right
             dtype=np.float32
        )

        self.vertex_count = 6

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
    
    def createColorBuffer(self):
        """
        Inicializa o 'frame buffer' customizado.
        """
        self.colorBufferData = np.array(
            [np.uint32((255<<16) + (255 << 8) + (255 << 0)) for pixel in range(WIDTH * HEIGHT)],
            dtype=np.uint32
        )
        
        self.colorBuffer = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.colorBuffer)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,HEIGHT,WIDTH,0,GL_RGBA,
                     GL_UNSIGNED_INT_8_8_8_8,bytes(self.colorBufferData))
    
    def createShader(self, vertexFilepath, fragmentFilepath):
        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader

    def ray_cast(self):
        glUseProgram(self.shader)

        # Limpa a tela para um novo frame
        self.clearScreen()

        posX, posY = self.game.player.pos
        dirX, dirY = PLAYER_DIR
        planoX, planoY = PLANO
        
        for rayIndex in range(WIDTH):
            cameraX = 2.0 * rayIndex / WIDTH - 1.0  # máximo = 1.0, quando rayIndex é aprox. WIDTH
                                                    # mínimo = -1.0, quando rayIndex == 0
            rayDirectionX = dirX + cameraX * planoX
            rayDirectionY = dirY + cameraX * planoY
            mapX, mapY = self.game.player.map_pos

            #distância delta: distância até o próxima reta X (horizontal) 
            # ou Y (vertical) no quadriculado.
            if np.abs(rayDirectionX) < 1e-8:
                deltaDistX = 1e8
            else:
                deltaDistX = abs(1/rayDirectionX)  
            
            if np.abs(rayDirectionY) < 1e-8:
                deltaDistY = 1e8
            else:
                deltaDistY = abs(1/rayDirectionY)
            
            if (rayDirectionX < 0):
                stepX = -1
                sideDistX = (posX - mapX) * deltaDistX
            else:
                stepX = 1
                sideDistX = (mapX + 1 - posX) * deltaDistX
            
            if (rayDirectionY < 0):
                stepY = -1
                sideDistY = (posY - mapY) * deltaDistY
            else:
                stepY = 1
                sideDistY = (mapY + 1 - posY) * deltaDistY
            
            while True:
                if (sideDistX < sideDistY):
                    sideDistX += deltaDistX
                    mapX += stepX
                    side = 0 # horizontal
                else:
                    sideDistY += deltaDistY
                    mapY += stepY
                    side = 1 # vertical
                
                if self.game.map.mini_map[mapY][mapX] != 0:
                    break
                
            if side == 0:
                distanceToCamera = np.abs(sideDistX - deltaDistX)
            else:
                distanceToCamera = np.abs(sideDistY - deltaDistY)
                
            self.drawVerticalLine(
                x = rayIndex,
                height = (HEIGHT//2)/max(distanceToCamera,1e-8),
                color = self.colors[self.game.map.mini_map[mapY][mapX] - 1]
            )
            
        self.updateScreen()

    def clearScreen(self):
        self.colorBufferData &= 0
        self.colorBufferData |= ((16 << 24) + (32 << 16) + (64 << 8) + 255)
    
    def drawVerticalLine(self, x, height, color):
        lineHeight = min(int(height), HEIGHT//2)
        wallTop = HEIGHT//2 - lineHeight + x * HEIGHT
        wallBottom = HEIGHT//2 + lineHeight + x * HEIGHT
        self.colorBufferData[wallTop:wallBottom] = color
    
    def updateScreen(self):
        glBindTexture(GL_TEXTURE_2D, self.colorBuffer)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,HEIGHT,WIDTH,0,GL_RGBA,
                     GL_UNSIGNED_INT_8_8_8_8,bytes(self.colorBufferData))
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))
        glDeleteTextures(1, (self.colorBuffer,))
        glDeleteProgram(self.shader)
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))
        glDeleteBuffers(self.shader)

    def update(self):
        self.ray_cast()
        
        