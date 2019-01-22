# denite-keymap
[denite.nvim](https://github.com/Shougo/denite.nvim) source for keymap.

## Requirements
- Neovim
    - exists('*nvim_get_keymap') && exists('*nvim_buf_get_keymap')
- denite.nvim

## Usage
```vim
:Denite keymap "all mode keymap
:Denite keymap:n "normal mode keymap
```

## Actions
- delete(unmap)
- execute(normal mode only)
- open,drop,tabopen
