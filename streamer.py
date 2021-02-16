#!/usr/bin/python3
# File Name: streamer.py
# Author: F.a.Leistra
# Date: 05-02-2021
# Desrc: Main file for the crypto trader (simulation)


import pandas as pd
from binance.client import Client
from datetime import datetime
import time
import sys


def check_candle(open, close):
    '''Function that checks the difference between the opening and closing value
    of a candle. The function returns 1 if the candle closed higher than opened and
    vice versa'''

    value = float(close) - float(open)
    if value > 0:
        return 1
    else:
        return -1

def get_candle_data(client, sign):
    '''Function that will make sure all data gets obtained from the binance API'''

    while True:
        candles = client.get_historical_klines(sign, Client.KLINE_INTERVAL_1MINUTE, "2 min ago UTC")
        if len(candles) == 2:
            break
        else:
            print('not all data obtained, waiting 2 secs')
            time.sleep(2)

    return candles


def main():

    client = Client('222f7FGVWJ6EVdwFA71gx67QuQK4p5pkU3oEgXZqgAmNGEcLmfhfZSxBtSrVG0aX',
                    '9Ta87I5ky0lN0cDOGM1KrdGJlXGzVJ65dagEQySDY43yp9WHUhhIsXHtpnPjxD8K')

    # Testing the connectivity
    print(client.ping())

    # Assinging the BTC symbol
    BTC = 'BTCUSDT'

    # Obtaining the order book
    order_book = client.get_order_book(symbol=BTC)

    print(order_book.keys())

    candles = client.get_historical_klines(BTC, Client.KLINE_INTERVAL_1MINUTE, "2 min ago UTC")

    # infitine loop
    #  - tijd 1 min verder -> candles ophalen
    #  - afgelopen 9 candles vergelijken met stijns patronen
    #  - 10 met 15 vergelijken
    #  - wanneer een patroon wordt gevonden een simulatie bet plaatsen
    #  - uitkomst van die bet opslaan

    patterns = []

    for c in candles:
        print(c)
        print(c[0] / 1000)
        print('Time:', datetime.utcfromtimestamp(c[0] / 1000).strftime('%Y-%m-%d %H:%M:%S'))
        print('Open:', c[1])
        print('High:', c[2])
        print('Low:', c[3])
        print('Close:', c[4])
        value = float(c[4]) - float(c[1])
        print(value)
        if value > 0:
            print('green', 1)
        else:
            print('red', -1)

        patterns.append(value)

    patterns = {
        '[1, -1, 1, -1, 1, -1, -1, 1, -1]': 'down',  # 1
        '[-1, -1, -1, -1, 1, -1, 1, -1, -1]': 'down',  # 2
        '[-1, -1, 1, -1, 1, -1, 1, -1, 1]': 'down',  # 3
        '[1, -1, -1, 1, 1, -1, 1, -1, 1]': 'down',  # 4
        '[1, -1, 1, -1, 1, -1, 1, -1, -1]': 'down',  # 5
        '[1, -1, 1, -1, 1, 1, 1, -1, -1]': 'down',  # 6
        '[1, -1, 1, 1, 1, 1, 1, -1, 1]': 'down',  # 7
        '[1, 1, 1, -1, 1, -1, -1, -1, 1]': 'down',  # 8
        '[1, 1, 1, -1, 1, -1, 1, 1, -1]': 'down',  # 9
        '[1, 1, 1, 1, 1, -1, 1, -1, 1]': 'down',  # 10
        '[-1, -1, -1, 1, -1, 1, -1, -1, 1]': 'up',  # 11
        '[-1, 1, 1, -1, -1, 1, -1, 1, -1]': 'up',  # 12
        '[-1, 1, -1, 1, 1, 1, -1, -1, 1]': 'up',  # 13
        '[-1, -1, -1, -1, -1, 1, -1, -1, 1]': 'up',  # 14
        '[-1, 1, -1, 1, -1, 1, -1, 1, -1]': 'up',  # 15
        '[-1, 1, -1, 1, -1, 1, -1, -1, -1]': 'up',  # 16
        '[1, 1, -1, 1, -1, 1, 1, 1, -1]': 'up',  # 17
        '[1, 1, 1, 1, -1, -1, -1, -1, -1]': 'up',  # 18
        '[-1, 1, 1, 1, -1, 1, -1, -1, -1]': 'up',  # 19
        '[-1, 1, 1, 1, 1, 1, -1, 1, -1]': 'up'}  # 20

    for i in patterns.keys():
        i = i.strip('][').split(', ')

    time_count = 0
    pattern_storage = []
    cash = 1000
    multiplier = 125


    with open('status_log.txt', 'w+') as f:
        f.write('Trade History:\n')

    count = 0
    while True:
        print('--- Initiating Loop ---')
        print('This is wat the pattern storage looks like: {}'.format(pattern_storage))
        candles = get_candle_data(client, BTC)
        # Loop for checking the time
        while True:
            candles1 = get_candle_data(client, BTC)
            if candles[1][0] == candles1[0][0]:
                print(candles)
                print(candles1)
                print('binance minute has passed')
                print(candles[0][0])
                print(candles1[1][0])
                count += 1
                break

            else:
                time.sleep(1)

        # Main loop for making the trades, this loop will only be reached if a minute has passed
        print('back in main loop, checking if we have reached 3 iterations.')
        print(count)

        open_candle = candles1[0][1]
        close_candle = candles1[0][4]

        # Determining the situation
        print('checking outcome of {} and {}'.format(open_candle, close_candle))
        candle_outcome = check_candle(open_candle, close_candle)
        print('outcome is {}'.format(candle_outcome))
        pattern_storage.append(candle_outcome)
        print(pattern_storage)

        time_count += 1

        # Checking if the storgae contains enough values for a possible pattern
        if len(pattern_storage) == 9:
            # Checking if the pattern exists in our dictionary
            if str(pattern_storage) in patterns:
                outcome = patterns[str(pattern_storage)]
                print('------------------ A PATTERN HAS BEEN FOUND -------------------')

                bet_size = 0.1 * cash
                cash -= bet_size
                bet_count = 0

                while True:
                    candles2 = get_candle_data(client, BTC)
                    if candles1[1][0] == candles2[0][0]:
                        # 1 minute has passed
                        bet_count += 1
                        if bet_count == 1:
                            close_price = candles2[0][4]

                        if bet_count == 5:
                            final_price = candles2[0][4]
                            final_outcome = float(final_price) - float(close_price)
                            break

                        else:
                            time.sleep(5)

                # bet was down
                if outcome == 'down':
                    if float(final_price) < float(close_price):
                        # bet was correct
                        correct = True
                        cash += (-final_outcome * multiplier * bet_size) + bet_size
                    else:
                        # bet was incorrect
                        correct = False
                        cash += (final_outcome * multiplier * bet_size) + bet_size

                # bet was up
                else:
                    if float(final_price) > float(close_price):
                        # bet was corect
                        correct = True
                        cash += (final_outcome * multiplier * bet_size) + bet_size
                    else:
                        # bet was incorrect
                        correct = False
                        cash += (-final_outcome * multiplier * bet_size) + bet_size

                print('Bet: {}, Outcome: {}, Cash: {}'.format(outcome, correct, cash))

                with open('status_log.txt', 'a') as f:
                    f.write('pattern detected {} - Bet outcome is {} - Correct: {} - Cash: {}\n'
                            .format(str(pattern_storage), outcome, correct, cash))
                pattern_storage.clear()
            else:
                time.sleep(1)

            if len(pattern_storage) > 0:
                pattern_storage.pop(0)

        print('-------- COMPLETED ONE ITERATION ---------')
        if count == 120:
            print('exiting...')
            break


if __name__ == "__main__":
    main()