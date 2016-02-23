" skeletons/templates when open new files
autocmd BufNewFile *.c{,c} 0r ~/.vim/skeleton/c.skel
autocmd BufNewFile *.c{pp,xx} 0r ~/.vim/skeleton/cpp.skel
"autocmd BufNewFile *.h{,pp} 0r ~/.vim/skeleton/h.skel
function! s:insert_gates()
	let gatename = "__" . substitute(toupper(expand("%:t")), "[\\.\\-]", "_", "g") . "__"
	execute "normal! i/**\n */\n"
	execute "normal! o#ifndef " . gatename
	execute "normal! o#define " . gatename . "\n\n"
	execute "normal! o#endif  // " . gatename
	execute "normal! o// vim:ts=4 sts=4 sw=4"
	normal! kk
endfunction
autocmd BufNewFile *.h{,pp} call <SID>insert_gates()
autocmd BufNewFile {M,m}akefile 0r ~/.vim/skeleton/makefile.skel
autocmd BufNewFile *.py 0r ~/.vim/skeleton/py.skel
autocmd BufNewFile *.sh 0r ~/.vim/skeleton/sh.skel
