class RadarPos:
	def __init__(self, code = None):
		self.geolat=0
		self.geolon=0
		self.recrise=0
		self.bmsep=0
		self.boresite=0
		self.alt = 300
		self.code = ''
		self.rsep = 45
		self.st_id = None
		if code is not None:
			if code == 'gbr': # goose bay
				self.st_id = 1
			elif code == 'kap': # kapuskasing
				self.st_id = 3
			elif code == 'hal': # halley bay
				self.st_id = 4
			elif code == 'sas': # saskatoon
				self.st_id = 5
			elif code == 'pgr': # British Columbia
				self.st_id = 6
			elif code == 'kod': # kodiak
				self.st_id = 7
			elif code == 'sto': # stokkseyri
				self.st_id = 8
			elif code == 'pyk': # pykkvibaer
				self.st_id = 9
			elif code == 'han': # Hankasalmi finland
				self.st_id = 10
			elif code == 'san': # sanae
				self.st_id = 11
			elif code == 'sys': # syowa
				self.st_id = 12
			elif code == 'sye': # syowa
				self.st_id = 13
			elif code == 'tig': # tiger
				self.st_id = 14
			elif code == 'ker': # Kerguelen
				self.st_id = 15
			elif code == 'ksr': # King Salmon
				self.st_id = 16
			elif code == 'unw': # tiger NZ (Unwin)
				self.st_id = 18
			elif code == 'zho': # Zho...?
				self.st_id = 19
			elif code == 'mcm': # McMurdo
				self.st_id = 20
			elif code == 'fir': # Falkland Islands
				self.st_id = 21
			elif code == 'sps': # South Pole
				self.st_id = 22
			elif code == 'wal': # Wallops Island
				self.st_id = 32
			elif code == 'bks': # BlackStone
				self.st_id = 33
			elif code == 'hok': # Hokkaido
				self.st_id = 40
			elif code == 'inv': # Inuvik
				self.st_id = 64
			elif code == 'rkn': # Rankin Inlet
				self.st_id = 65
			elif code == 'svb': # Svalbard
				self.st_id = 128
			elif code == 'fhw': # FH West
				self.st_id = 204
			elif code == 'fhe': # FH East
				self.st_id = 205
			elif code == 'cvw': # CV West
				self.st_id = 206
			elif code == 'cve': # CV East
				self.st_id = 207
			elif code == 'adw': # Adak West
				self.st_id = 208
			elif code == 'ade': # Adak East
				self.st_id = 209
			elif code == 'azw': #Christmas Valley West
				self.st_id = 210
			elif code == 'aze': #Christmas Valley East
				self.st_id = 211
		if self.st_id == 1: # goose bay
			self.geolat=+53.32
			self.geolon=-60.46
			self.boresite=5.0
			self.bmsep=3.24
			self.recrise=0.0
			self.code = 'gbr'
		elif self.st_id == 3: # kapuskasing
			self.geolat=+49.39
			self.geolon=-82.32
			self.boresite=-12.00
			self.bmsep=3.24
			self.recrise=100.0
			self.code = 'kap'
		elif self.st_id == 4: # halley bay
			self.geolat=-75.52
			self.geolon=-26.63
			self.boresite=5.0
			self.bmsep=-3.24
			self.recrise=200.0
			self.code = 'hal'
		elif self.st_id == 5: # saskatoon
			self.geolat=+52.16
			self.geolon=-106.53
			self.boresite=23.10
			self.bmsep=3.24
			self.recrise=0.0
			self.code = 'sas'
		elif self.st_id == 6: # British Columbia
			self.geolat=+55.
			self.geolon=-125.
			self.boresite=-15.0
			self.bmsep=3.24
			self.recrise=0.0
			self.code = 'pgr'
		elif self.st_id == 7: # kodiak
			self.geolat=+57.6
			self.geolon=-152.2
			self.boresite=30.0
			self.bmsep=3.24
			self.recrise=100.0
			self.code = 'kod'
		elif self.st_id == 8: # stokkseyri
			self.geolat=+63.86
			self.geolon=-22.02
			self.boresite=-59.0
			self.bmsep=3.29
			self.recrise=100.0
			self.code = 'sto'
		elif self.st_id == 9: # pykkvibaer
			self.geolat=+63.77
			self.geolon=-20.54
			self.boresite=+30.0
			self.bmsep=3.24
			self.recrise=100.0
			self.code = 'pyk'
		elif self.st_id == 10: # Hankasalmi finland
			self.geolat=+62.32
			self.geolon=+26.61
			self.boresite=-12.0
			self.bmsep=3.24
			self.recrise=100.0
			self.code = 'han'
		elif self.st_id == 11: # sanae
			self.geolat=-72
			self.geolon=-3
			self.boresite=170.0
			self.bmsep=-3.24
			self.recrise=100.0
			self.code = 'san'
		elif self.st_id == 12: # syowa
			self.geolat=-69.0
			self.geolon=+39.58
			self.boresite=159.0
			self.bmsep=-3.33
			self.recrise=100.0
			self.code = 'sys'
		elif self.st_id == 13: # syowa
			self.geolat=-69.0
			self.geolon=+39.58
			self.boresite=107.0
			self.bmsep=-3.33
			self.recrise=50.0
			self.code = 'sye'
		elif self.st_id == 14: # tiger
			self.geolat=-43.38
			self.geolon=+147.23
			self.boresite=180.0
			self.bmsep=-3.24
			self.recrise=100.0
			self.code = 'tig'
		elif self.st_id == 15: # Kerguelen
			self.geolat=-49.35
			self.geolon=+70.26
			self.boresite=168.0
			self.bmsep=-3.24
			self.recrise=100.0
			self.code = 'ker'
		elif self.st_id == 16: # King Salmon
			self.geolat=58.68
			self.geolon=-156.65
			self.boresite=-25.0
			self.bmsep=3.24
			self.recrise=100.0
			self.code = 'ksr'
		elif self.st_id == 18: # tiger NZ (Unwin)
			self.geolat=-46.51
			self.geolon=168.38
			self.boresite=227.9
			self.bmsep=-3.24
			self.recrise=100.0
			self.code = 'unw'
		elif self.st_id == 19: # Zho...?
			self.geolat=-69.378
			self.geolon=+76.377
			self.boresite=72.5
			self.bmsep=+3.24
			self.recrise=100.0
			self.code = 'zho'
		elif self.st_id == 20: # McMurdo
			self.geolat=-77.88
			self.geolon=166.73
			self.boresite=+263.4
			self.bmsep=+3.24
			self.recrise=100.0
			self.code = 'mcm'
		elif self.st_id == 21: # Falkland Islands
			self.geolat=-51.83
			self.geolon=-58.98
			self.boresite=+178.2
			self.bmsep=-3.24
			self.recrise=100.0
			self.code = 'fir'
		elif self.st_id == 22: # South Pole
			self.geolat=-89.995
			self.geolon=+118.291
			self.boresite=+75.709
			self.bmsep=+3.24
			self.recrise=100.0
			self.code = 'sps'
		elif self.st_id == 32: # Wallops Island
			self.geolat=+37.93
			self.geolon=-75.47
			self.boresite=35.86
			self.bmsep=+3.24
			self.recrise=100.0
			self.code = 'wal'
		elif self.st_id == 33: # BlackStone
			self.geolat=+37.10
			self.geolon=-77.95
			self.boresite=32.0
			self.bmsep=+3.86
			self.recrise=100.0
			self.code = 'bks'
		elif self.st_id == 40: # Hokkaido
			self.geolat=+43.53
			self.geolon=+143.61
			self.boresite=30.0
			self.bmsep=+3.24
			self.recrise=100.0
			self.code = 'hok'
		elif self.st_id == 64: # Inuvik
			self.geolat=+68.420
			self.geolon=-133.5
			self.boresite=+29.5
			self.bmsep=+3.24
			self.recrise=100.0
			self.code = 'inv'
		elif self.st_id == 65: # Rankin Inlet
			self.geolat=+62.82
			self.geolon=-93.11
			self.boresite=+8.73
			self.bmsep=+3.24
			self.recrise=100.0
			self.code = 'rkn'
		elif self.st_id == 128: # Svalbard
			self.geolat=+75.15
			self.geolon=+16.05
			self.boresite=25.
			self.bmsep=+3.24
			self.recrise=100.0
			self.code = 'svb'
		elif self.st_id == 204: # FH West
			self.geolat=+38.859
			self.geolon=-99.389
			self.boresite=-25.
			self.bmsep=+3.24
			self.recrise=100.0
			self.code = 'fhw'
		elif self.st_id == 205: # FH East
			self.geolat=+38.859
			self.geolon=-99.389
			self.boresite=+45.
			self.bmsep=+3.24
			self.recrise=100.0
			self.code = 'fhe'
		elif self.st_id == 206: # CV West
			self.geolat=+43.271
			self.geolon=-120.358
			self.boresite=-20.
			self.bmsep=+3.24
			self.recrise=100.0
			self.code = 'cvw'
		elif self.st_id == 207: # CV East
			self.geolat=+43.271
			self.geolon=-120.358
			self.boresite=+54.
			self.bmsep=+3.24
			self.recrise=100.0
			self.code = 'cve'
		elif self.st_id == 208: # Adak West
			self.geolat=+51.89
			self.geolon=-176.63
			self.boresite=-28.
			self.bmsep=+3.24
			self.recrise=100.0
			self.code = 'adw'
		elif self.st_id == 209: # Adak East
			self.geolat=+51.89
			self.geolon=-176.63
			self.boresite=+46.0
			self.bmsep=+3.24
			self.recrise=100.0
			self.code = 'ade'
		elif self.st_id == 210: #Christmas Valley West
			self.geolat=+51.89
			self.geolon=-176.63
			self.boresite=+46.
			self.bmsep=+3.24
			self.recrise=100.0
			self.code = 'azw'
		elif self.st_id == 211: #Christmas Valley East
			self.geolat=+51.89
			self.geolon=-176.63
			self.boresite=+46.
			self.bmsep=+3.24
			self.recrise=100.0
			self.code = 'aze'
			
		else:
			self.geolat=+53.32
			self.geolon=-60.46
			self.boresite=5.0
			self.bmsep=3.24
			self.recrise=50.0
			self.code = 'tst'
