import matplotlib.pyplot as plt
import numpy as np
import copy
from mpl_toolkits.axes_grid1 import make_axes_locatable


def cbviewer(volume):
    """ image-viewer for the representation of several 3D volumes

    on iMac:
    %matplotlib tk
    """

    plt.style.use('ggplot')
    k = 0
    for i, entry in enumerate(volume):
        if len(entry[0].shape) == 4:
            k += entry[0].shape[3]
        else:
            k += 1
    nImages = k

    size = volume[0][0].shape[0:2]
    factor = 10/size[0]
    ywidth = factor * size[1]

    ## maximum number arrays display
    if nImages > 16:
        nImages = 16
        volume = volume[0:nImages]

    ## set up grid
    if nImages == 1:
        fig, axs = plt.subplots(1,1, figsize=(ywidth,10), sharey=True,
                                sharex=True, constrained_layout=True)
        axs = np.array(axs)
    elif nImages == 2:
        fig, axs = plt.subplots(1,2, figsize=(ywidth * 2,10), sharey=True,
                                sharex=True, constrained_layout=True)
    elif nImages > 2 and nImages < 5:
        fig, axs = plt.subplots(2,2, figsize=(ywidth * 2,20), sharey=True,
                                sharex=True, constrained_layout=True)
    elif nImages > 4 and nImages < 7:
        fig, axs = plt.subplots(2,3, figsize=(ywidth * 3,20), sharey=True,
                                sharex=True, constrained_layout=True)
    elif nImages > 6 and nImages < 9:
        fig, axs = plt.subplots(2,4, figsize=(ywidth * 4,20), sharey=True,
                                sharex=True, constrained_layout=True)
    elif nImages > 8 and nImages < 13:
        fig, axs = plt.subplots(3,4, figsize=(ywidth * 4,30), sharey=True,
                                sharex=True, constrained_layout=True)
    elif nImages > 12:
        fig, axs = plt.subplots(4,4, figsize=(ywidth * 4,40), sharey=True,
                                sharex=True, constrained_layout=True)

    axs = np.ndarray.flatten(axs)

    k = -1
    for i, entry in enumerate(volume):
        if len(entry[0].shape) == 4:
            for j in range(entry[0].shape[3]):
                tmpentry = copy.deepcopy(entry)
                tmpentry[0] = entry[0][..., j]
                tmpdict = entry[1]
                if 'title' in tmpdict:
                    tmpentry[1]['title'] = entry[1]['title'] + ', Dyn ' + str(j+1)
                k += 1
                if k < 16:
                    plot_entry(k, tmpentry, fig, axs)
        else:
            k += 1
            plot_entry(k, entry, fig, axs)

    for i in range(len(axs)):
        axs[i].axis('off')

    fig.canvas.mpl_connect('key_press_event', lambda event: process_key(event, nImages))
    fig.canvas.mpl_connect('scroll_event', lambda event: process_scroll(event, nImages))
    fig.show()


def plot_entry(i, entry, fig, axs):
    tmpimg = np.transpose(entry[0], [2, 0, 1])
    aspect = 'equal'
    if len(entry) == 2:
        tmpdict = entry[1]
        if 'voxelSize_mm' in tmpdict:
            voxelSize_mm = tmpdict['voxelSize_mm']
            cor_aspect = voxelSize_mm[2]/voxelSize_mm[0]
            sag_aspect = voxelSize_mm[2]/voxelSize_mm[1]
            trans_aspect = voxelSize_mm[1]/voxelSize_mm[0]
        else:
            sag_aspect = 'equal'
            cor_aspect = 'equal'
            trans_aspect = 'equal'
        if 'plane' in tmpdict:
            if tmpdict['plane'] == 'coronal':
                tmpimg = np.transpose(entry[0], [0, 2, 1])
                tmpimg = np.flip(tmpimg, axis=[1, 2])
                aspect = cor_aspect
            elif tmpdict['plane'] == 'sagittal':
                tmpimg = np.transpose(entry[0], [1, 2, 0])
                tmpimg = np.flip(tmpimg, axis=1)
                aspect = sag_aspect
            elif tmpdict['plane'] == 'transverse':
                tmpimg = np.transpose(entry[0], [2, 0, 1])
                aspect = trans_aspect
            else:
                print('The plane you selected is not available, choose from: coronal, sagittal, transverse')
    axs[i].index = tmpimg.shape[0] // 2
    axs[i].volume = tmpimg
    gray = plt.get_cmap('gray')

    if len(entry) == 1:
        a = axs[i].imshow(tmpimg[axs[i].index], cmap=gray, aspect=aspect)
    if len(entry) == 2:
        if 'slice' in tmpdict:
            slice_index = tmpdict['slice']-1
            if slice_index >= 0 and slice_index < tmpimg.shape[0]:
                axs[i].index = slice_index
            else:
                print('The slice you selected is not available, choose from 1 to {}.'.format(tmpimg.shape[0]))

        if 'cmap' in tmpdict:
            try:
                cmap = plt.get_cmap(tmpdict['cmap'])
            except ValueError as e:
                print('The cmap you selected is not available, choose from:')
                print(e)
                cmap = gray
        else:
            cmap = gray

        if 'window' in tmpdict:
            a = axs[i].imshow(tmpimg[axs[i].index],
                              vmin=tmpdict['window'][0],
                              vmax=tmpdict['window'][1],
                              cmap=cmap, aspect=aspect)
        else:
            a = axs[i].imshow(tmpimg[axs[i].index], cmap=cmap, aspect=aspect)

        if 'title' in tmpdict:
            axs[i].set_title(tmpdict['title'])

        divider = make_axes_locatable(axs[i])
        cax = divider.append_axes("right", size="5%", pad=0.05)

        if 'clabel' in tmpdict:
            fig.colorbar(a, cax=cax, label=tmpdict['clabel'])
        else:
            fig.colorbar(a, cax=cax)

    t = axs[i].text(0,0,'slice: ' + str(axs[i].index + 1) + '/' +
                    str(tmpimg.shape[0]), verticalalignment = 'top',
                    horizontalalignment = 'center', transform=axs[i].transAxes)
    t.set_bbox(dict(facecolor='white', edgecolor='white'))


def process_scroll(event, nImages):
    fig = event.canvas.figure
    for i, ax in enumerate(fig.axes):
        if i >= nImages:
            continue
        else:
            if event.button == 'down':
                previous_slice(ax)
            elif event.button == 'up':
                next_slice(ax)
    fig.canvas.update()
    fig.canvas.flush_events()


def process_key(event, nImages):
    fig = event.canvas.figure
    for i, ax in enumerate(fig.axes):
        if i >= nImages:
            continue
        else:
            if event.key == 'j':
                previous_slice(ax)
            elif event.key == 'k':
                next_slice(ax)
    fig.canvas.update()
    fig.canvas.flush_events()


def previous_slice(ax):
    volume = ax.volume
    ax.index = (ax.index - 1) % volume.shape[0]  # wrap around using %
    ax.images[0].set_array(volume[ax.index])
    ax.texts[0]._text = 'slice: ' + str(ax.index + 1) + '/' + str(volume.shape[0])
    ax.draw_artist(ax.texts[0])
    ax.draw_artist(ax.images[0])


def next_slice(ax):
    volume = ax.volume
    ax.index = (ax.index + 1) % volume.shape[0]
    ax.images[0].set_array(volume[ax.index])
    ax.texts[0]._text = 'slice: ' + str(ax.index + 1) + '/' + str(volume.shape[0])
    ax.draw_artist(ax.texts[0])
    ax.draw_artist(ax.images[0])


def remove_keymap_conflicts(new_keys_set):
    for prop in plt.rcParams:
        if prop.startswith('keymap.'):
            keys = plt.rcParams[prop]
            remove_list = set(keys) & new_keys_set
            for key in remove_list:
                keys.remove(key)
