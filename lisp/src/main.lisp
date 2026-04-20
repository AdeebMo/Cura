(let* ((script-path (or *load-truename* *compile-file-truename*))
       (script-directory (make-pathname :name nil :type nil :defaults script-path)))
  (load (merge-pathnames "text-utils.lisp" script-directory))
  (load (merge-pathnames "lexicon.lisp" script-directory))
  (load (merge-pathnames "normalizer.lisp" script-directory)))

(defun inventory-mode-p ()
  (member "--inventory" sb-ext:*posix-argv* :test #'string=))

(if (inventory-mode-p)
    (format t "~s~%" (canonical-inventory))
    (let ((input (read-input)))
      (format t "~s~%" (normalize-input input))))
