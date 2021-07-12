import math
import serial
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

class Box:
	def __init__(self, pos, size):
		self.pos = [0, 0, 0]
		self.size = size
		self.angleVec = [0, 0, 0, 0]

		self.verticies = [
			[pos[0]-size[0]/2., pos[1]+size[1]/2., pos[2]-size[2]/2.],
			[pos[0]+size[0]/2., pos[1]+size[1]/2., pos[2]-size[2]/2.],
			[pos[0]+size[0]/2., pos[1]-size[1]/2., pos[2]-size[2]/2.],
			[pos[0]-size[0]/2., pos[1]-size[1]/2., pos[2]-size[2]/2.],

			[pos[0]-size[0]/2., pos[1]+size[1]/2., pos[2]+size[2]/2.],
			[pos[0]+size[0]/2., pos[1]+size[1]/2., pos[2]+size[2]/2.],
			[pos[0]+size[0]/2., pos[1]-size[1]/2., pos[2]+size[2]/2.],
			[pos[0]-size[0]/2., pos[1]-size[1]/2., pos[2]+size[2]/2.]
		]

		self.edges = [
			[0, 1],
			[0, 3],
			[0, 4],
			[1, 2],
			[1, 5],
			[2, 3],
			[2, 6],
			[3, 7],
			[4, 5],
			[5, 6],
			[6, 7],
			[7, 4]
		]

	def move(self, vec):
		self.pos[0] += vec[0]
		self.pos[1] += vec[1]
		self.pos[2] += vec[2]

	def rotate(self, ang, vec):
		self.angleVec[0] += ang
		self.angleVec[1] += vec[0]
		self.angleVec[2] += vec[1]
		self.angleVec[3] += vec[2]

	def draw(self):
		glPushMatrix()

		glTranslatef(*self.pos)
		glRotatef(*self.angleVec)

		glBegin(GL_LINES)
		for edge in self.edges:
			for vertex in edge:
				glVertex3fv(self.verticies[vertex])
		glEnd()

		glPopMatrix()


def normalize(v, res):
	return [v[0]/res[0] - 0.5, v[1]/res[1] - 0.5, 1]

def vecMul(v1, v2):
	return [v1[i] * v2[i] for i in range(len(v1))]


def main():
	pygame.init()
	display = (800,600)
	pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

	gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

	myBox = Box([0, 0, 0], [1., 0.5, 2.]);
	# testBox = Box([0, 0, 0], [1., 0.5, 3.]);
	camera_dir = [0, 0, 0]

	glTranslatef(0.0, -0.3, -4)

	mouse_pos = pygame.mouse.get_pos()
	prev_mouse_pos = [*mouse_pos]
	lastPosX = 0
	lastPosY = 0

	move_cof = 0.002

	move_sens = [2.0, 3.0]
	move_div = 100.

	rotate_cof = 50.
	data_round = 10

	ser = serial.Serial('/dev/cu.wchusbserial14110', 115200)
	print(ser.name)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				ser.close()
				pygame.quit()
				quit()
				
		mouse_pos = pygame.mouse.get_pos()
		if pygame.mouse.get_pressed()[0]:
			if pygame.key.get_pressed()[pygame.K_LSHIFT]:
				mouse_mov = [mouse_pos[0] - prev_mouse_pos[0], mouse_pos[1] - prev_mouse_pos[1]]
				if (mouse_mov[0] > 0) or (mouse_mov[1] > 0):
					modelView = (GLfloat * 16)()
					mvm = glGetFloatv(GL_MODELVIEW_MATRIX, modelView)

					temp = (GLfloat * 3)();
					temp[0] = modelView[0]*mouse_mov[1] + modelView[1]*mouse_mov[0]
					temp[1] = modelView[4]*mouse_mov[1] + modelView[5]*mouse_mov[0]
					temp[2] = modelView[8]*mouse_mov[1] + modelView[9]*mouse_mov[0]
					norm_xy = math.sqrt(temp[0]*temp[0] + temp[1]*temp[1] + temp[2]*temp[2])
					# glRotatef(math.sqrt(mouse_mov[0]**2 + mouse_mov[1]**2), temp[0]/norm_xy, temp[1]/norm_xy, temp[2]/norm_xy)
					myBox.rotate(math.sqrt(mouse_mov[0]**2 + mouse_mov[1]**2), [temp[0]/norm_xy, temp[1]/norm_xy, temp[2]/norm_xy])

			else:
				glTranslatef(move_cof*(mouse_pos[0] - prev_mouse_pos[0]), -move_cof*(mouse_pos[1] - prev_mouse_pos[1]), 0)
		prev_mouse_pos = [*mouse_pos]

		dpos = str(ser.readline())[2:-5].split(' ')
		dmove = []
		for i in range(len(dpos)):
			dmove.append(math.floor(float(dpos[i])*data_round)/data_round if float(dpos[i]) >= 0 else math.ceil(float(dpos[i])*data_round)/data_round)
		print(dmove)

		# FOR ACCEL MOVING LOCALLY
		myBox.move([-dmove[4]/move_div if math.fabs(dmove[4]) > move_sens[1] else 0., 0., dmove[3]/move_div if math.fabs(dmove[3]) > move_sens[0] else 0.])


		# FOR GYRO ROTOATION
		# if math.fabs(dmove[0]) > 0:
		# 	glRotatef(-math.degrees(dmove[0])/rotate_cof, 0., 0., 1.) 
		# if math.fabs(dmove[1]) > 0:
		# 	glRotatef(-math.degrees(dmove[1])/rotate_cof, 0., 1., 0.)
		# if math.fabs(dmove[2]) > 0:
		# 	glRotatef(math.degrees(dmove[2])/rotate_cof, 1., 0., 0.)




		if pygame.key.get_pressed()[pygame.K_1]:
			glScalef(0.95, 0.95, 0.95)
		elif pygame.key.get_pressed()[pygame.K_2]:
			glScalef(1.05, 1.05, 1.05)


		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

		myBox.draw()
		# testBox.draw()

		pygame.display.flip()
		pygame.time.wait(10)


if __name__ == '__main__':
	main()