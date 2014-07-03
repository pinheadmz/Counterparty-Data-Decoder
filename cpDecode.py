import sys
import struct
import binascii

# protocol constants
# NOTE: using latest protocol only  -- 	"issue" valid for blocks > 283271 only
#										"dividend" valid for blocks > 288150 only
PREFIX = 'CNTRPRTY'
TXTYPE_FORMAT = '>I'
TXTYPE = {
0  : {'type': 'send', 'FORMAT' : '>QQ', 'details' : ('asset_id', 'quantity')},
10 : {'type': 'order', 'FORMAT' : '>QQQQHQ', 'details' : ('give_id', 'give_quantity', 'get_id', 'get_quantity', 'expiration', 'fee_required')},
11 : {'type': 'BTCpay', 'FORMAT' : '>32s32s', 'details' : ('tx0_hash_bytes', 'tx1_hash_bytes')},
20 : {'type': 'issue', 'FORMAT' : '>QQ??If42p', 'details' : ('asset_id', 'quantity', 'divisible', 'callable_', 'call_date', 'call_price', 'description')},
21 : {'type': 'callback', 'FORMAT' : '>dQ', 'details' : ('fraction', 'asset_id')},
30 : {'type': 'broadcast', 'FORMAT' : '>IdI52p', 'details' : ('timestamp', 'value', 'fee_fraction_int', 'text')},
40 : {'type': 'bet', 'FORMAT' : '>HIQQdII', 'details' : ('bet_type', 'deadline', 'wager_quantity', 'counterwager_quantity', 'target_value', 'leverage', 'expiration')},
50 : {'type': 'dividend', 'FORMAT' : '>QQQ', 'details' : ('quantity_per_unit', 'asset_id', 'dividend_asset_id')},
60 : {'type': 'burn', 'FORMAT' : '>QQQ', 'details' : None},
70 : {'type': 'cancel', 'FORMAT' : '>32s', 'details' : ('offer_hash_bytes')},
80 : {'type': 'rps', 'FORMAT' : '>HQ32sI', 'details' : ('possible_moves', 'wager', 'move_random_hash', 'expiration')},
81 : {'type': 'rps resolve', 'FORMAT' : '>H16s32s32s', 'details' : ('move', 'random', 'tx0_hash_bytes', 'tx1_hash_bytes')}
}

# convert integer to Base26 string
def base26decode(i):
	if i == 0 : return 'BTC'
	if i == 1 : return 'XCP'
	b26_digits = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	res = []
	n = i
	while n > 0:
		n, r = divmod (n, 26)
		res.append(b26_digits[r])
	asset_name = ''.join(res[::-1])
	return asset_name

# grab command-line parameter and convert to byte array from utf-8 encoded hex string
data = sys.argv[1]
databytes = binascii.unhexlify(bytes(data, 'utf-8'))

#### iterate through byte array and decode ####
# get data length and pop off that byte
dLength = databytes[0]
dChunk = databytes[1: dLength + 1]

# get protocol prefix and pop that off
dPrefix = dChunk[:len(PREFIX)]
dChunk = dChunk[len(PREFIX):]


# message data & metadata
dType = struct.unpack(TXTYPE_FORMAT, dChunk[:4])[0]
dMessage = dChunk[4:]
txFormat = TXTYPE[dType]
txUnpacked = list(struct.unpack(txFormat['FORMAT'], dMessage))

# match up data from message with format labels
txDetails = {'type' : txFormat['type']}
for i, v in enumerate(txUnpacked):
	txDetails[txFormat['details'][i]] = v

# output
print('Length Byte: ', dLength)
print('Prefix Bytes: ', dPrefix)
print('TX type Byte: ', dType)
for key in txDetails:
	if key == 'asset_id':
		val = base26decode(txDetails[key])
	elif key in ('quantity', 'give_quantity', 'get_quantity', 'wager_quantity', 'counterwager_quantity'):
		val = txDetails[key] / 100000000
	else:
		val = txDetails[key]
	
	print(key + ':', val)