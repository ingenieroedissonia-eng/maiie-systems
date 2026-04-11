
from pathlib import Path
path = Path(chr(99)+chr(111)+chr(110)+chr(102)+chr(105)+chr(103)+chr(47)+chr(112)+chr(114)+chr(111)+chr(109)+chr(112)+chr(116)+chr(115)+chr(47)+chr(97)+chr(114)+chr(99)+chr(104)+chr(105)+chr(116)+chr(101)+chr(99)+chr(116)+chr(46)+chr(116)+chr(120)+chr(116))
c = path.read_text(encoding=chr(117)+chr(116)+chr(102)+chr(45)+chr(56))
old = chr(45)+chr(32)+chr(80)+chr(82)+chr(79)+chr(72)+chr(73)+chr(66)+chr(73)+chr(68)+chr(79)+chr(32)+chr(108)+chr(105)+chr(115)+chr(116)+chr(97)+chr(114)+chr(32)+chr(101)+chr(108)+chr(32)+chr(109)+chr(105)+chr(115)+chr(109)+chr(111)
print(old in c)
