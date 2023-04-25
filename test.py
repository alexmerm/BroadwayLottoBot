#%%
from Telecharge import Telecharge

tc = Telecharge()


# %%
# shows = tc.getShows()
toGet = {"ANDREW LLOYD WEBBER'S BAD CINDERELLA" :2,
"BOB FOSSE'S DANCIN'" : 1,
'KIMBERLY AKIMBO' : 2,
'PETER PAN GOES WRONG' :2
}
tc.enterLotteries(toGet)
# %%
