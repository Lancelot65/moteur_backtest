import ccxt, pandas as pd, indicateur_techniques as id, numpy as np, matplotlib.pyplot as plt
sys.path.append('Ohlcvplus/ohlcv')
from ohlcv import OhlcvPlus

class Backtest:
	def __init__(self, capital):
		self.capital_initial = capital
		self.capital = capital

		self.positions_long = []
		self.quantite_position_long = []

		self.positions_short = []
		self.quantite_position_short = []

		self.trade_short_pc = []
		self.trade_long_pc = []

		self.trade_short_v = []
		self.trade_long_v = []


	def load_data(self, symbol='BTC/USDT', time='30m', length=500, sinces='2023-01-01 00:00:00'):
		#telecharcgement des donnée ohlcv
		ohlcvp = OhlcvPlus(ccxt.binance(), database_path='data.db')
		self.data = ohlcvp.load(market=symbol, timeframe=time, since=sinces, limit=length, update=True, verbose=True, workers=100)
		
	def open_long(self, close, pos, quantite=0.1):
		if not self.positions_long:
			self.positions_long.append(close)
			self.quantite_position_long.append(self.capital * quantite)
			print("open_long", close, "   ", pos)
			self.append_element_df("long_open", pos)
	
	def close_long(self, close, position, test=0):
		if self.positions_long:
			for pos in range(len(self.positions_long)):
				self.capital += (close - self.positions_long[pos]) * self.quantite_position_long[pos] # - (self.positions_long[pos] * self.quantite_position_long[pos] * 0.3
				
				self.trade_long_pc.append(((close / self.positions_long[pos]) - 1) * 100)
				self.trade_long_v.append((close - self.positions_long[pos]) * self.quantite_position_long[pos])
			self.append_element_df("long_close", position)


			self.positions_long.clear()
			self.quantite_position_long.clear()
			"""
			if test == 1:
				print("close garce au take_profit", close, "   ", position)
			elif test == 2:
				print("close garce au stop_loss", close, "   ", position)
			elif test == 0:
				print("close_long")
				print(close, "   ", position)
			else:
				print("choix_incorrect", test)
			"""
	def open_short(self, close, pos, quantite=0.1):
		if not self.positions_short:
			self.positions_short.append(close)
			self.quantite_position_short.append(self.capital * quantite)
			print("open_short", close, "   ", pos)
			self.append_element_df("short_open", pos)
	
	def close_short(self, close, position, test=0):
		if self.positions_short:
			for pos in range(len(self.positions_short)):
				self.capital += (self.positions_short[pos] - close)  * self.quantite_position_short[pos] # - (self.positions_short[pos] * self.quantite_position_short[pos] * 0.3)
				self.trade_short_pc.append(((self.positions_short[pos] / close) - 1) * 100)
				self.trade_short_v.append((self.positions_short[pos] - close) * self.quantite_position_short[pos])

			self.append_element_df("short_close", position)
			

			self.positions_short.clear()
			self.quantite_position_short.clear()
			"""
			
			if test == 1:
				print("close garce au take_profit", close, "   ", position)
			elif test == 2:
				print("close garce au stop_loss", close, "   ", position)
			elif test == 0:
				print("close_short", close, "   ", position)
			else:
				print("choix_incorrect", test)
			"""
				
	def show_evolution_price(self):
		self.data.evolution_price.plot()
	
	def update(self, pos, close):
		"""
		close_actuel
		"""
		self.take_profit(close, pos)
		self.stop_loss(close, pos)
		self.data.at[pos, 'evolution_price'] = self.capital
		if self.positions_long:
			print("___  ", ((close / self.positions_long[0]) - 1) * 100, "  ___")
		if self.positions_short:
			print("***  ", ((self.positions_short[0] / close) - 1) * 100, "  ***")
		
	def take_profit(self, close, position):
		if self.positions_long:
			
			if ((close / self.positions_long[0]) - 1) * 100 > 2:
				print("take_profit_long")
				print(((close / self.positions_long[0]) - 1) * 100)
				self.close_long(close, position, 1)
				
	
		if self.positions_short:
			if ((close / self.positions_short[0]) - 1) * 100 < -2:
				print("take_profit_short")
				print(((close / self.positions_short[0]) - 1) * 100)
				self.close_short(close, position, 1)
	
	def stop_loss(self, close, position):
		
		if self.positions_long:
			if ((close / self.positions_long[0]) - 1) * 100 < -1:
				print("stop_loss_long")
				print(((close / self.positions_long[0]) - 1) * 100)
				self.close_long(close, position, 2)

		if self.positions_short:
			if ((close / self.positions_short[0]) - 1) * 100 > 1:
				print("stop_loss_short")
				print(((close / self.positions_short[0]) - 1) * 100)
				self.close_short(close, position, 2)
	
	def stat_final(self):
		self.rendement = ((self.capital - self.capital_initial) / self.capital_initial) * 100
		print(f"Votre capital a évoluer de {self.rendement}%, avec une valeur initiale de {self.capital_initial}$ à {self.capital}$ soit une évolution de {self.capital_initial - self.capital}$")

		print(f"total trade : {len(self.trade_long_v) + len(self.trade_short_v)}")
		print(f"nombre long_trade : {len(self.trade_long_v)}")
		print(f"nombre short_trade : {len(self.trade_short_v)}")

		a, b = 0, 0
		for element in self.trade_long_v:
			if element > 0:
				a +=1
			elif element < 0:
				b += 1
		print(f"trade_long_win : {a}")
		print(f"trade_long_lose : {b}")

		a, b = 0, 0
		for element in self.trade_short_v:
			if element > 0:
				a +=1
			elif element < 0:
				b += 1
		print(f"trade_short_win : {a}")
		print(f"trade_short_lose : {b}")

		print(f"moyenne long_trade : {sum(self.trade_long_v) / len(self.trade_long_v)}$ / {sum(self.trade_long_pc) / len(self.trade_long_pc)}%")
		print(f"moyenne short_trade : {sum(self.trade_short_v) / len(self.trade_short_v)}$ / {sum(self.trade_short_pc) / len(self.trade_short_pc)}%")

		print(f"best long_trade : {max(self.trade_long_v)}$ / {max(self.trade_long_pc)}%")
		print(f"best short_trade : {max(self.trade_short_v)}$ / {max(self.trade_short_pc)}%")

		print(f"bad long_trade : {min(self.trade_long_v)}$ / {min(self.trade_long_pc)}%")
		print(f"bad short_trade : {min(self.trade_short_v)}$ / {min(self.trade_short_pc)}%")

	
	def append_element_df(self, style:str, position):
		"""
		style doit être égale a :
		-short_open
		-short_close
		-long_open
		-long_close
		et position a ou on est dans le df
		"""
		if style == "short_open":
			self.data.at[position, 'position_short_open'] = True
		elif style == "short_close":
			self.data.at[position, 'position_short_close'] = True
		elif style == "long_open":
			self.data.at[position, 'position_long_open'] = True
		elif style == "long_close":
			self.data.at[position, 'position_long_close'] = True
		else:
			print("Error, the style is not correct")
	
	def graphique(self, list_indicateur:list):
		#lsit_indicateur doit contenir les df de tout les indicateur utiliser
		positions_so = np.where(self.data.position_short_open == True)[0]
		positions_sc = np.where(self.data.position_short_close == True)[0]
		positions_lo = np.where(self.data.position_long_open == True)[0]
		positions_lc = np.where(self.data.position_long_close == True)[0]

		for indicateur in list_indicateur:
			indicateur.plot()
		
		move = self.data.close.mean() * 0.0007
		for pos in positions_so:
			x = pos
			y = self.data.close[pos]
			plt.plot(x, y+move,'o', marker='v', markersize=7, label='Triangles', color='green')
		for pos in positions_sc:
			x = pos
			y = self.data.close[pos]
			plt.plot(x, y+move,'o', marker='v', markersize=7, label='Triangles', color='red')
		for pos in positions_lo:
			x = pos
			y = self.data.close[pos]
			plt.plot(x, y-move,'o', marker='^', markersize=7, label='Triangles', color='green')
		for pos in positions_lc:
			x = pos
			y = self.data.close[pos]
			plt.plot(x, y-move,'o', marker='^', markersize=7, label='Triangles', color='red')
		self.data.close.plot()
	
	def trier_signal(self, series):
		result = []
		current_value = None
		for value in series:
			if value == current_value:
				result.append(None)
			else:
				current_value = value
				result.append(value)
		result[0] = None
		return result