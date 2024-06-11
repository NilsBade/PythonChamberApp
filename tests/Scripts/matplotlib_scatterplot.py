import matplotlib.pyplot as plt

fig, ax = plt.subplots()

sc = ax.scatter([1, 2], [1, 2], c=[1, 2])
ax.set_ylabel('YLabel', loc='top')
ax.set_xlabel('XLabel', loc='left')
cbar = fig.colorbar(sc)
cbar.set_label("ZLabel", loc='top')

cbar.remove()
plt.delaxes(sc)
#fig, ax = plt.subplots()
new = ax.scatter([2,10,5], [2,11,6], c=[0,100, 50])
cbar2 = fig.colorbar(new)

plt.show()