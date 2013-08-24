# Back is used for the scrolling image...
class Back(pygame.sprite.Sprite):
	def __init__(self,name):
		pygame.sprite.Sprite.__init__(self)
		self.tendency = 0
		self.image, self.rect = load_image(name+'.jpg')