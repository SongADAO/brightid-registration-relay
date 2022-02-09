BRIGHTID_ABI = '[{"type":"constructor","stateMutability":"nonpayable","inputs":[{"type":"address","name":"_verifierToken","internalType":"contract IERC20"},{"type":"bytes32","name":"_app","internalType":"bytes32"}]},{"type":"event","name":"OwnershipTransferred","inputs":[{"type":"address","name":"previousOwner","internalType":"address","indexed":true},{"type":"address","name":"newOwner","internalType":"address","indexed":true}],"anonymous":false},{"type":"event","name":"Sponsor","inputs":[{"type":"address","name":"addr","internalType":"address","indexed":true}],"anonymous":false},{"type":"event","name":"Verified","inputs":[{"type":"address","name":"addr","internalType":"address","indexed":true}],"anonymous":false},{"type":"event","name":"VerifierTokenSet","inputs":[{"type":"address","name":"verifierToken","internalType":"contract IERC20","indexed":false}],"anonymous":false},{"type":"function","stateMutability":"view","outputs":[{"type":"uint32","name":"","internalType":"uint32"}],"name":"REGISTRATION_PERIOD","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"bytes32","name":"","internalType":"bytes32"}],"name":"app","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"history","inputs":[{"type":"address","name":"","internalType":"address"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"bool","name":"","internalType":"bool"}],"name":"isVerifiedUser","inputs":[{"type":"address","name":"_user","internalType":"address"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"owner","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"renounceOwnership","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"setVerifierToken","inputs":[{"type":"address","name":"_verifierToken","internalType":"contract IERC20"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"sponsor","inputs":[{"type":"address","name":"addr","internalType":"address"}]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"transferOwnership","inputs":[{"type":"address","name":"newOwner","internalType":"address"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"time","internalType":"uint256"},{"type":"bool","name":"isVerified","internalType":"bool"}],"name":"verifications","inputs":[{"type":"address","name":"","internalType":"address"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"contract IERC20"}],"name":"verifierToken","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"verify","inputs":[{"type":"address[]","name":"addrs","internalType":"address[]"},{"type":"uint256","name":"timestamp","internalType":"uint256"},{"type":"uint8","name":"v","internalType":"uint8"},{"type":"bytes32","name":"r","internalType":"bytes32"},{"type":"bytes32","name":"s","internalType":"bytes32"}]}]'

BRIGHTID_NODE = 'https://app.brightid.org/node/v5'

VERIFICATIONS_URL = BRIGHTID_NODE + '/verifications'

RPC_URL = 'wss://idchain.one/ws/'

NOT_FOUND = 2
NOT_SPONSORED = 4

CHAINID = '0x4a'
GAS = 500000
GAS_PRICE = 10000000000

LINK_CHECK_NUM = 18
LINK_CHECK_PERIOD = 10
SPONSOR_CHECK_NUM = 6
SPONSOR_CHECK_PERIOD = 10
