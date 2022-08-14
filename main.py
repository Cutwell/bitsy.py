import matplotlib.pyplot as plt
from bitsy import Test, Engine, GraphicsSystem

world = Test.test3()
e = Engine()
world = e.parseWorld(world)

import json
del world['tune']
del world['blip']
# save the world to a file
with open('test3world.json', 'w') as f:
    f.write(json.dumps(world, indent=4))

#g = GraphicsSystem(world)
#g.start()
#plt.show()