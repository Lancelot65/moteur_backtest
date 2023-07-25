import ccxt, pandas as pd, numpy as np, matplotlib.pyplot as plt, sys
sys.path.append('../Ohlcvplus/ohlcv')
from ohlcv import OhlcvPlus

class Backtest:
	def __init__(self, capital):
		self.capital_initial = capital
		self.capital = capital

		self.positions_long = None
		self.quantite_position_long = None

		self.positions_short = None
		self.quantite_position_short = None

		self.trade_short_pc = []
		self.trade_long_pc = []

		self.trade_short_v = []
		self.trade_long_v = []

		self.va_take_profit_long = None
		self.va_take_profit_short = None
		self.va_stop_loss_long = None
		self.va_stop_loss_short = None

	def load_data(self, symbol='BTC/USDT', time='30m', length=500, sinces='2023-01-01 00:00:00'):
		#telecharcgement des donnée ohlcv
		ohlcvp = OhlcvPlus(ccxt.binance(), database_path='data.db')
		self.data = ohlcvp.load(market=symbol, timeframe=time, since=sinces, limit=length, update=True, verbose=True, workers=100)
		
	def open_long(self, close, pos, montant, take_profit=None, stop_loss=None):
		if self.positions_long is None:
			self.positions_long = close
			self.quantite_position_long = montant / close
			
			print("open_long", close, "   ", pos)
			self.append_element_df("long_open", pos)

			if take_profit is not None:
				self.va_take_profit_long = close * (1 + (take_profit / 100))
			else:
				self.va_take_profit_long = None
			if stop_loss is not None:
				self.va_stop_loss_long = close * (1 - (stop_loss / 100))
			else:
				self.va_stop_loss_long = None
	
	def close_long(self, close, position, test=0):
		if self.positions_long is not None:
			print("___  ", ((close / self.positions_long) - 1) * 100, "  ___")
			self.capital += (close - self.positions_long) * self.quantite_position_long # - (self.positions_long * self.quantite_position_long * 0.3
			
			self.trade_long_pc.append(((close / self.positions_long) - 1) * 100)
			self.trade_long_v.append((close - self.positions_long) * self.quantite_position_long)
			self.append_element_df("long_close", position)


			self.positions_long = None
			self.quantite_position_long = None
			
			if test == 1:
				print("close garce au take_profit", close, "   ", position)
			elif test == 2:
				print("close grace au stop_loss", close, "   ", position)
			elif test == 0:
				print("close_long")
				print(close, "   ", position)
			else:
				print("choix_incorrect", test)
			
	def open_short(self, close, pos, montant, take_profit=None, stop_loss=None):
		if self.positions_short is None:
			self.positions_short = close
			self.quantite_position_short = montant / close
			
			print("open_short", close, "   ", pos)
			self.append_element_df("short_open", pos)

			if take_profit is not None:
				self.va_take_profit_short = close * (1 - (take_profit / 100))
			else:
				self.va_take_profit_short = None
			if stop_loss is not None:
				self.va_stop_loss_short = close * (1 + (stop_loss / 100))
			else:
				self.va_stop_loss_short = None


	
	def close_short(self, close, position, test=0):
		if self.positions_short is not None:
			print("***  ", ((self.positions_short / close) - 1) * 100, "  ***")
			self.capital += (self.positions_short - close) * self.quantite_position_short # - (self.positions_short * self.quantite_position_short * 0.3)
			self.trade_short_pc.append(((self.positions_short / close) - 1) * 100)
			self.trade_short_v.append((self.positions_short - close) * self.quantite_position_short)

			self.append_element_df("short_close", position)
			

			self.positions_short = None
			self.quantite_position_short = None
			
			
			if test == 1:
				print("close grace au take_profit", close, "   ", position)
			elif test == 2:
				print("close grace au stop_loss", close, "   ", position)
			elif test == 0:
				print("close_short", close, "   ", position)
			else:
				print("choix_incorrect", test)
							
	def show_evolution_price(self):
		self.data.evolution_price.plot()
	
	def update(self, pos, close):
		"""
		close_actuel
		"""
		self.take_profit(close, pos)
		self.stop_loss(close, pos)
		self.data.at[pos, 'evolution_price'] = self.capital
		
	def take_profit(self, close, position):
		if self.va_take_profit_long is not None:
			
			if self.va_take_profit_long < close:
				print("take_profit_long")
				print(self.va_take_profit_long)
				self.close_long(close, position, 1)
				self.va_take_profit_long = None
				
	
		if self.va_take_profit_short is not None:
			if self.va_take_profit_short > close:
				print("take_profit_short")
				print(self.va_take_profit_short)
				self.close_short(close, position, 1)
				self.va_take_profit_short = None
	

	def stop_loss(self, close, position):		
		if self.va_stop_loss_long is not None:
			if self.va_stop_loss_long > close:
				print("stop_loss_long")
				print(self.va_stop_loss_long)
				self.close_long(close, position, 2)
				self.va_stop_loss_long = None

		if self.va_stop_loss_short is not None:
			if self.va_stop_loss_short < close:
				print("stop_loss_short")
				print(self.va_stop_loss_short)
				self.close_short(close, position, 2)
				self.va_stop_loss_short = None
	
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
	
	def stat_final(self):
		self.rendement = ((self.capital - self.capital_initial) / self.capital_initial) * 100
		print(f"Votre capital a évoluer de {round(self.rendement, 3)}%, avec une valeur initiale de {self.capital_initial}$ à {round(self.capital, 2)}$ soit une évolution de {round(self.capital - self.capital_initial, 2)}$")

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

		try:
			print(f"moyenne long_trade : {round(sum(self.trade_long_v) / len(self.trade_long_v), 2)}$ / {round(sum(self.trade_long_pc) / len(self.trade_long_pc), 2)}%")
		except (ZeroDivisionError, ValueError):
			print("moyenne long_trade : 0$ / 0%")
		try:
			print(f"moyenne short_trade : {round(sum(self.trade_short_v) / len(self.trade_short_v), 2)}$ / {round(sum(self.trade_short_pc) / len(self.trade_short_pc), 2)}%")
		except (ZeroDivisionError, ValueError):
			print("moyenne short_trade : 0$ / 0%")

		try:
			print(f"best long_trade : {round(max(self.trade_long_v), 2)}$ / {round(max(self.trade_long_pc), 2)}%")
		except (ZeroDivisionError, ValueError):
			print("best long_trade : 0$ / 0%")
		try:
			print(f"best short_trade : {round(max(self.trade_short_v), 2)}$ / {round(max(self.trade_short_pc), 2)}%")
		except (ZeroDivisionError, ValueError):
			print("best short_trade : 0$ / 0%")

		try:
			print(f"bad long_trade : {round(min(self.trade_long_v), 2)}$ / {round(min(self.trade_long_pc), 2)}%")
		except (ZeroDivisionError, ValueError):
			print("bad long_trade : 0$ / 0%")
		try:
			print(f"bad short_trade : {round(min(self.trade_short_v), 2)}$ / {round(min(self.trade_short_pc), 2)}%")
		except (ZeroDivisionError, ValueError):
			print("bad short_trade : 0$ / 0%")

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
		try:
			positions_so = np.where(self.data.position_short_open == True)[0]
		except AttributeError:
			positions_so = []

		try:
			positions_sc = np.where(self.data.position_short_close == True)[0]
		except AttributeError:
			positions_sc = []

		try:
			positions_lo = np.where(self.data.position_long_open == True)[0]
		except AttributeError:
			positions_lo = []

		try:
			positions_lc = np.where(self.data.position_long_close == True)[0]
		except AttributeError:
			positions_lc = []

		for indicateur in list_indicateur:
			indicateur.plot()
		
		for pos in positions_so:
			x = pos
			y = self.data.close[pos]
			plt.plot(x, y,'o', marker='v', markersize=10, label='Triangles', color='green')
		for pos in positions_sc:
			x = pos
			y = self.data.close[pos]
			plt.plot(x, y,'o', marker='v', markersize=10, label='Triangles', color='red')
		for pos in positions_lo:
			x = pos
			y = self.data.close[pos]
			plt.plot(x, y,'o', marker='^', markersize=10, label='Triangles', color='green')
		for pos in positions_lc:
			x = pos
			y = self.data.close[pos]
			plt.plot(x, y,'o', marker='^', markersize=10, label='Triangles', color='red')
		self.data.close.plot(color='black', linewidth=1)