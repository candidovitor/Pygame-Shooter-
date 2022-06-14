import pygame
import os
import random
import csv
import button

pygame.init()

TELA_LARGURA = 800
TELA_ALTURA = int(TELA_LARGURA * 0.8)

tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
pygame.display.set_caption('JOGO EM PYGAME')

relogio = pygame.time.Clock()
FPS = 60
LIXO = 200
GRAVIDADE = 0.75
TERRA_TAMANHO = 40
LINHAS = 16
COLUNAS = 150
TERRA_TAMANHO = TELA_ALTURA // LINHAS
COISAS_TIPO = 21
tela_rolar = 0
bg_rolar = 0
level = 1 

start_game = False

movimento_esquerda = False
movimento_direita = False
atirar = False
granada = False
granada_jogada = False

start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()

painel1_img = pygame.image.load('img/background/pine1.png').convert_alpha()
painel2_img = pygame.image.load('img/background/pine2.png').convert_alpha()
montanha_img = pygame.image.load('img/background/mountain.png').convert_alpha()
nuvem_img = pygame.image.load('img/background/sky_cloud.png').convert_alpha()



img_list = []
for x in range(COISAS_TIPO):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img, (TERRA_TAMANHO, TERRA_TAMANHO))
    img_list.append(img)


bala_img = pygame.image.load('img/icons/bullet.copy.png').convert_alpha()
granada_img = pygame.image.load('img/icons/grenade.png').convert_alpha()

health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
municao_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
granada_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()

item_caixas = {
    'vida' : health_box_img,
    'municao': municao_box_img,
    'granada': granada_box_img
}

BG = (255, 255, 102)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
AZUL_LEGAL = (65, 105, 225)

font = pygame.font.SysFont('Futura', 25)
def desenhar_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    tela.blit(img, (x,y))


def desenho_background():
    tela.fill(AZUL_LEGAL)
    width = nuvem_img.get_width()
    for x in range(5):
        tela.blit(nuvem_img, ((x * width) - bg_rolar * 0.5, 0))
        tela.blit(montanha_img,((x * width) - bg_rolar * 0.6, TELA_LARGURA - montanha_img.get_height()-300))
        tela.blit(painel1_img,((x * width) - bg_rolar * 0.7, TELA_LARGURA - painel1_img.get_height()-150))
        tela.blit(painel2_img,((x * width) - bg_rolar * 0.8, TELA_LARGURA - painel2_img.get_height()))

def reiniciar_nivel():
    inimigo_grupo.empty()
    bala_grupo.empty()
    granada_grupo.empty()
    explode_grupo.empty()
    item_caixa_grupo.empty()
    decoracao_grupo.empty()
    agua_grupo.empty()
    saida_grupo.empty()
    world_data = []

    data = []
    for linhas in range(LINHAS):
        l = [-1] * COLUNAS
        world_data.append(l)
    return data



class soldado(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y,scale, velocidade, municao, granada):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.velocidade = velocidade
        self.municao = municao
        self.inicio_municao = municao
        self.shoot_cooldown = 0
        self.granada = granada
        self.saude = 100
        self.maximo_vida = self.saude
        self.direcao = 1
        self.vel_y = 0
        self.pular = False
        self.no_ar = True
        self.virar = False
        self.animacao_lista = []
        self.frame_index = 0
        self.acao = 0
        self.atualizar_tempo = pygame.time.get_ticks()
        self.move_counter = 0
        self.visao = pygame.Rect(0, 0, 150, 20)
        self.ocioso = False
        self.ocioso_counter = 0


        animacao_tipo = ['Idle', 'Run', 'Jump', 'Death']
        for animacao in animacao_tipo:
            temp_list = []
            numero_de_frames = len(os.listdir(f'img/{self.char_type}/{animacao}'))
            for i in range(numero_de_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animacao}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animacao_lista.append(temp_list)

        

        self.image = self.animacao_lista[self.acao][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def atualizar(self):
        self.atualizar_animacao()
        self.checar_a_vida()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


    def movimento(self, movimento_esquerda, movimento_direita):
        tela_rolar = 0
        dx = 0
        dy = 0
        
        if movimento_esquerda:
            dx = - self.velocidade
            self.virar = True
            self.direcao = -1

        if movimento_direita:
            dx = self.velocidade
            self.virar = False
            self.direcao = 1

        if self.pular == True and self.no_ar == False:
            self.vel_y = -11 
            self.pular = False
            self.no_ar = True

        self.vel_y += GRAVIDADE
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        for terra in mundo.obstaculo_list:
            if terra[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0

                if self.char_type == 'inimigo':
                    self.direcao *= -1
                    self.movimento_counter = 0

            if terra[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = terra[1].bottom - self.rect.top

                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.no_ar = False
                    dy = terra[1].top - self.rect.bottom
        
        if pygame.sprite.spritecollide(self, agua_grupo, False):
            self.saude = 0

        if self.rect.bottom > TELA_ALTURA:
            self.saude = 0

        if self.char_type == 'jogador':
            if self.rect.left + dx < 0 or self.rect.right + dx> TELA_LARGURA:
                dx = 0

        self.rect.x += dx
        self.rect.y += dy
        

        if self.char_type == 'jogador':
            if (self.rect.right > TELA_LARGURA - LIXO and bg_rolar < (mundo.nivel_lenght * TERRA_TAMANHO) - TELA_LARGURA) or (self.rect.left < LIXO and bg_rolar > abs(dx)):
                self.rect.x -= dx
                tela_rolar = -dx
        return tela_rolar

        


    def atirar(self):
        if self.shoot_cooldown == 0 and self.municao > 0:
            self.shoot_cooldown = 20
            bala = Bala(self.rect.centerx + (0.6 * self.rect.size[0] * self.direcao), self.rect.centery, self.direcao)
            bala_grupo.add(bala)
            self.municao -= 1


    def ai(self):
        if self.alive and jogador.alive:
            if self.ocioso == False and random.randint(1, 200) == 1:
                self.atualizar_acao(0)
                self.ocioso = True
                self.ocioso_counter = 50
            if self.visao.colliderect(jogador.rect):
                self.atualizar_acao(0)
                self.atirar()
            else:
                if self.ocioso == False:
                    if self.direcao == 1:
                        ai_inimigo_direita = True
                    else:
                        ai_inimigo_direita = False
                    ai_inimigo_esquerda = not ai_inimigo_direita
                    self.movimento(ai_inimigo_esquerda, ai_inimigo_direita)
                    self.atualizar_acao(1)
                    self.move_counter += 1

                    self.visao.center = (self.rect.centerx + 75 * self.direcao, self.rect.centery)
                    if self.move_counter > TERRA_TAMANHO:
                        self.direcao *= -1
                        self.move_counter *= -1
                else: 
                    self.ocioso_counter -=1
                    if self.ocioso_counter <= 0:
                        self.ocioso = False
                    
        self.rect.x += tela_rolar 

    def atualizar_animacao(self):
        ANIMACAO_FRESH = 100
        
        self.image = self.animacao_lista[self.acao][self.frame_index]
        

        if pygame.time.get_ticks() - self.atualizar_tempo > ANIMACAO_FRESH:
            self.atualizar_tempo = pygame.time.get_ticks()
            self.frame_index += 1
        
        if self.frame_index >= len(self.animacao_lista[self.acao]):
            if self.acao == 3:
                self.frame_index = len(self.animacao_lista[self.acao]) -1
            else:
                self.frame_index = 0


    def atualizar_acao(self, new_action):
        if new_action != self.acao:
            self.acao = new_action
            self.frame_index = 0
            self.atualizar_tempo = pygame.time.get_ticks()
    
    def checar_a_vida(self):
        if self.saude <= 0:
            self.saude = 0
            self.velocidade = 0
            self.alive = False
            self.atualizar_acao(3)
  
    def desenho(self):
        tela.blit(pygame.transform.flip(self.image, self.virar, False), self.rect)
        
        
class Mundo():
    def __init__(self):
        self.obstaculo_list = []


    def processo_data(self, data):
        self.nivel_lenght = len(data[0])
        for y, linha in enumerate(data):
            for x, terra in enumerate(linha):
                if terra >= 0:
                    img = img_list[terra]
                    img_rect = img.get_rect()
                    img_rect.x = x * TERRA_TAMANHO
                    img_rect.y = y * TERRA_TAMANHO
                    world_data = (img, img_rect)

                    if terra >= 0 and terra <= 8:
                        self.obstaculo_list.append(world_data)
                    elif terra >= 9 and terra <= 10:
                        agua = Agua(img, x * TERRA_TAMANHO, y * TERRA_TAMANHO)
                        agua_grupo.add(agua)
                    elif terra >= 11 and terra <= 14:
                        decoracao = Decoracao(img, x * TERRA_TAMANHO, y * TERRA_TAMANHO)
                        decoracao_grupo.add(decoracao)
                    elif terra == 15:
                        jogador = soldado('jogador',x * TERRA_TAMANHO, y * TERRA_TAMANHO, 1.65, 5, 20, 5)
                        barra_vida = Barra_Vida(10, 10, jogador.saude, jogador.saude)
                    elif terra == 16:
                        inimigo = soldado('inimigo', x * TERRA_TAMANHO, y * TERRA_TAMANHO, 1.65, 2, 20, 0)
                        inimigo_grupo.add(inimigo)
                    elif terra == 17:
                        item_caixa = ItemCaixa('municao', x * TERRA_TAMANHO, y * TERRA_TAMANHO)
                        item_caixa_grupo.add(item_caixa)
                    elif terra == 18:
                        item_caixa = ItemCaixa('granada', x * TERRA_TAMANHO, y * TERRA_TAMANHO)
                        item_caixa_grupo.add(item_caixa)
                    elif terra == 19:
                        item_caixa = ItemCaixa('vida', x * TERRA_TAMANHO, y * TERRA_TAMANHO)
                        item_caixa_grupo.add(item_caixa)
                    elif terra == 20:
                        sair = Saida(img, x * TERRA_TAMANHO, y * TERRA_TAMANHO)
                        saida_grupo.add(sair)
                        

        return jogador, barra_vida

    def draw(self):
        for terra in self.obstaculo_list:
            terra[1][0] += tela_rolar
            tela.blit(terra[0], terra[1])
        
class Agua(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TERRA_TAMANHO // 2, y + (TERRA_TAMANHO - self.image.get_height()))

    def update(self):
        self.rect.x += tela_rolar
    

class Saida(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TERRA_TAMANHO // 2, y + (TERRA_TAMANHO - self.image.get_height()))

    def update(self):
        self.rect.x += tela_rolar

class Decoracao(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TERRA_TAMANHO // 2, y + (TERRA_TAMANHO - self.image.get_height()))

    def update(self):
        self.rect.x += tela_rolar

class ItemCaixa(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_caixas[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TERRA_TAMANHO// 2, y + (TERRA_TAMANHO - self.image.get_height()))

    def update(self):
        self.rect.x += tela_rolar
        if pygame.sprite.collide_rect(self, jogador):
            if self.item_type == 'vida':
                jogador.saude += 25
                if jogador.saude > jogador.maximo_vida:
                    jogador.saude = jogador.maximo_vida
                    
            elif self.item_type == 'municao':
                jogador.municao += 10
            elif self.item_type == 'granada':
                jogador.granada += 2
            self.kill()
        


class Barra_Vida():
    def __init__(self, x, y, saude, maximo_vida):
        self.x = x
        self.y = y
        self.saude = saude
        self.maximo_vida = maximo_vida

    def desenhar_barra(self, saude):
            self.saude = saude
            pygame.draw.rect(tela, RED, (self.x, self.y, 150, 20))
            ratio = self.saude / self.maximo_vida
            pygame.draw.rect(tela, BLACK, (self.x - 2, self.y - 2, 154, 24))
            pygame.draw.rect(tela, RED, (self.x, self.y, 150, 20))
            pygame.draw.rect(tela, GREEN, (self.x, self.y, 150 * ratio, 20))




class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, direcao):
        pygame.sprite.Sprite.__init__(self)
        self.velocidade = 10
        self.image = bala_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direcao = direcao

    def update(self):
        self.rect.x += (self.direcao * self.velocidade) + tela_rolar
        if self.rect.right < 0 or self.rect.left > TELA_LARGURA:
            self.kill()


        if pygame.sprite.spritecollide(jogador, bala_grupo, False):
            if jogador.alive:
                jogador.saude -= 5
                self.kill()

        for inimigo in inimigo_grupo:
            if pygame.sprite.spritecollide(inimigo, bala_grupo, False):
                if inimigo.alive:
                    inimigo.saude -= 25
                    self.kill()


class Granada(pygame.sprite.Sprite):
    def __init__(self, x, y, direcao):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.velocidade = 7
        self.image = granada_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direcao = direcao

    def update(self):
        self.vel_y += GRAVIDADE
        dx = self.direcao * self.velocidade
        dy = self.vel_y

        for terra in mundo.obstaculo_list:
            if terra[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direcao *= -1
                dx = self.direcao * self.velocidade

                if terra[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    self.velocidade = 0

                    if self.vel_y < 0:
                        self.vel_y = 0
                        dy = terra[1].bottom - self.rect.top

                    elif self.vel_y >= 0:
                        self.vel_y = 0
                        dy = terra[1].top - self.rect.bottom
        

        if self.rect.left + dx < 0 or self.rect.right + dx >  TELA_LARGURA:
            self.direcao = self.direcao * int(-1)
            dx = self.direcao * self.velocidade

        self.rect.x += dx + tela_rolar
        self.rect.y += dy

        self.timer = self.timer -1
        if self.timer <= 0:
            self.kill()
            explosao = Explode(self.rect.x, self.rect.y, 0.5)
            explode_grupo.add(explosao)
            
            if abs(self.rect.centerx - jogador.rect.centerx) < TERRA_TAMANHO * 2 and \
                abs(self.rect.centery - jogador.rect.centery) < TERRA_TAMANHO * 2:
                jogador.saude -= 50 

            for inimigo in inimigo_grupo:
                if abs(self.rect.centerx - inimigo.rect.centerx) < TERRA_TAMANHO * 2 and \
                abs(self.rect.centery - inimigo.rect.centery) < TERRA_TAMANHO * 2:
                    inimigo.saude -= 50 


class Explode(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range (1,6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0  

    def update(self):
        self.rect.x += tela_rolar
        VELOCIDADE_EXPLOSAO = 4
        self.counter += 1

        if self.counter >= VELOCIDADE_EXPLOSAO:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]



start_buttom = button.Button(TELA_LARGURA // 2 - 130, TELA_ALTURA // 2 - 150, start_img, 1)
exit_buttom = button.Button(TELA_LARGURA // 2 - 110, TELA_ALTURA // 2 + 50, exit_img, 1)
restar_buttom = button.Button(TELA_LARGURA // 2 - 100, TELA_ALTURA // 2 - 50, restart_img, 2)

inimigo_grupo = pygame.sprite.Group()
bala_grupo = pygame.sprite.Group()
granada_grupo = pygame.sprite.Group()
explode_grupo = pygame.sprite.Group()
item_caixa_grupo = pygame.sprite.Group()
decoracao_grupo = pygame.sprite.Group()
agua_grupo = pygame.sprite.Group()
saida_grupo = pygame.sprite.Group()



world_data = []
for linhas in range(LINHAS):
    l = [-1] * COLUNAS
    world_data.append(l)

with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, linha in enumerate(reader):
        for y, terra in enumerate(linha):
            world_data[x][y] = int(terra)

print(world_data)

mundo = Mundo()
jogador, barra_vida = mundo.processo_data(world_data)

run = True
while run:
    relogio.tick(FPS)

    tela.fill(AZUL_LEGAL)

    if start_game == False:
        if start_buttom.draw(tela):
            start_game = True

        if exit_buttom.draw(tela):
            run = False
    else:
            
        desenho_background()
        mundo.draw()
        barra_vida.desenhar_barra(jogador.saude)

        desenhar_text('Munição: ', font, RED, 10, 40)
        for x in range(jogador.municao):
            tela.blit(bala_img, (90 + (x * 10), 40))

        desenhar_text('Granadas: ', font, RED, 10, 60)
        for x in range(jogador.granada):
            tela.blit(granada_img, (135 + (x * 15), 60))

        jogador.atualizar()
        jogador.desenho()

        for inimigo in inimigo_grupo:
            inimigo.atualizar()
            inimigo.desenho()
            inimigo.ai()

        bala_grupo.update()
        granada_grupo.update()
        explode_grupo.update()
        item_caixa_grupo.update()
        decoracao_grupo.update()
        agua_grupo.update()
        saida_grupo.update()

        bala_grupo.draw(tela) 
        granada_grupo.draw(tela)
        explode_grupo.draw(tela)
        item_caixa_grupo.draw(tela)
        decoracao_grupo.draw(tela)
        agua_grupo.draw(tela)
        saida_grupo.draw(tela)

        if jogador.alive:
            if atirar:
                jogador.atirar()
            
            elif granada and granada_jogada == False and jogador.granada > 0:
                granada = Granada(jogador.rect.centerx + (0.5 * jogador.rect.size[0] * jogador.direcao), jogador.rect.top, jogador.direcao)
                granada_grupo.add(granada)
                granada_jogada = True
                jogador.granada -= 1

                
            if jogador.no_ar:
                jogador.atualizar_acao(2)

            elif movimento_esquerda or movimento_direita:
                jogador.atualizar_acao(1)

            else:
                jogador.atualizar_acao(0)
            tela_rolar = jogador.movimento(movimento_esquerda, movimento_direita)
            bg_rolar -= tela_rolar

        else:
            tela_rolar = 0
            if restar_buttom.draw(tela):
                bg_rolar = 0

                mundo_dados = reiniciar_nivel()
                with open(f'level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, linha in enumerate(reader):
                        for y, terra in enumerate(linha):
                            world_data[x][y] = int(terra)
                
                mundo = Mundo()
                jogador, barra_vida = mundo.processo_data(world_data) 

    for event in pygame.event.get():
       
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                movimento_esquerda = True
            if event.key == pygame.K_d:
                movimento_direita = True
            if event.key == pygame.K_SPACE:
                atirar = True
            if event.key == pygame.K_e:
                granada = True
            if event.key == pygame.K_w and jogador.alive:
                jogador.pular = True
            if event.key == pygame.K_ESCAPE:
                run = False
       

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                movimento_esquerda = False

            if event.key == pygame.K_d:
                movimento_direita = False

            if event.key == pygame.K_SPACE:
                atirar = False
            
            if event.key == pygame.K_e:
                granada = False
                granada_jogada = False

    pygame.display.update()

pygame.quit()


