L = [1,2,3]

class A():
	def __init__(self):
		self.gg()

	def gg(self):
		L.append(555)
		print('----')
		print(L)

class B(A):
	def __init__(self):
		super().__init__()
		

class C(A):
	def __init__(self):
		super().__init__()


B()














C()