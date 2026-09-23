from pathlib import Path
import matplotlib as mpl
from matplotlib import font_manager
def configure_math():
    # Cambria Math is the second face in Windows' Cambria TTC. Extract only into
    # a private runtime cache; never distribute the system font with the paper.
    from fontTools.ttLib import TTCollection
    target=Path('D:/STUDY/My_github/sci_project/.tmp_complete_figures_20260920/CambriaMath.ttf')
    if not target.exists():TTCollection('C:/Windows/Fonts/cambria.ttc').fonts[1].save(target)
    font_manager.fontManager.addfont(target)
    mpl.rcParams.update({'mathtext.fontset':'custom','mathtext.rm':'Cambria Math','mathtext.it':'Cambria Math','mathtext.bf':'Cambria Math','mathtext.sf':'Cambria Math','mathtext.tt':'Cambria Math','mathtext.cal':'Cambria Math','mathtext.default':'rm','mathtext.fallback':None})
