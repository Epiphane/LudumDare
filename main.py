""" 
LUDUM DARE 27 ENTRY
8/23/2013 - 8/26/2013
THEME: 10 Seconds
BY: Thomas Steinke, Elliot Fiske, Eli Backer

May be uploaded to http://thomassteinke.net
or another domain later, if decided.

Bring it on, LD.

"""

# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
#                      INITIALIZE CLASSES AND GAME                       |
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
exec(open('init.py'))
exec(open('ui_class.py'))
exec(open('arena_mechanics.py'))
exec(open('camera.py'))
exec(open('character_class.py'))

def init():
	global font				# Font
	global player1, player2	# Players
	global currentArena		# Midpoint
	global camera			# duh
	global Import_sprite,interface		# RenderPlains

	font = pygame.font.Font("fonts/ka1.ttf", 30)
	
	player1 = Player(1, 8)
	player2 = Player(1, 9)
	currentArena = 8.5
	
	camera = Camera(currentArena)
	
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
#                                  MAIN LOOP                             |
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
init()
while 1:
	# USER INPUT
	deltat = clock.tick(50)
	
	# Check user input
	for event in pygame.event.get():
		if event.type is pygame.QUIT: sys.exit()
		if hasattr(event, 'key'):
			if event.key is K_ESCAPE: 
				if event.type is pygame.KEYDOWN: sys.exit()
			if event.key is K_a:
				if event.type is pygame.KEYDOWN: changeArena(currentArena - 1)
			if event.key is K_d:
				if event.type is pygame.KEYDOWN: changeArena(currentArena + 1)
				
	camera.update()
	camera.draw(screen)
						
	pygame.display.flip()