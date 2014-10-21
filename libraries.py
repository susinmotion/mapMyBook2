class Library:
	def __init__(self, name, address, number, accessible, latLng, ):
		self.name=name.strip
		self.address=address
		self.number=number
		self.accessible=accessible
		self.latLng=latLng
		self.status = None

	def __repr__(self):
		return "name="+self.name+" address= "+ self.address+ " number= "+ self.number+\
		"accessible= "+ str(self.accessible)+"latLng= "+str(self.latLng)

	def __str__(self):
		return self.name+self.address+self.number+str(self.accessible)+str(self.latLng)