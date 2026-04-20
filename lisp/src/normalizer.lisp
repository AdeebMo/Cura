(defun phrase-matches (normalized-text)
  (labels ((covered-by-existing-p (phrase accepted)
             (some
              (lambda (accepted-entry)
                (search phrase (first accepted-entry) :test #'char=))
              accepted))
           (collect-matches (remaining accepted)
             (if (null remaining)
                 (nreverse accepted)
                 (let* ((entry (car remaining))
                        (phrase (car entry))
                        (canonical (cdr entry)))
                   (if (and (search phrase normalized-text :test #'char=)
                            (not (covered-by-existing-p phrase accepted)))
                       (collect-matches (cdr remaining) (cons (list phrase canonical) accepted))
                       (collect-matches (cdr remaining) accepted))))))
    (collect-matches *phrase-synonyms* '())))

(defun phrase-words (phrase-results)
  (dedupe-preserving-order
   (apply #'append
          (mapcar
           (lambda (phrase-result)
             (split-sequence #\Space (first phrase-result)))
           phrase-results))))

(defun token-matches (tokens)
  (remove nil
          (mapcar
           (lambda (token)
             (let ((match (assoc token *word-synonyms* :test #'string=)))
               (when match
                 (cdr match))))
           tokens)))

(defun unknown-terms (tokens phrase-results)
  (let ((matched-words (phrase-words phrase-results)))
    (remove-if
     (lambda (token)
       (or (assoc token *word-synonyms* :test #'string=)
           (member token *stopwords* :test #'string=)
           (member token matched-words :test #'string=)))
     tokens)))

(defun read-input ()
  (with-output-to-string (buffer)
    (loop for line = (read-line *standard-input* nil nil)
          while line do
            (write-string line buffer)
            (write-char #\Space buffer))))

(defun normalize-input (raw-text)
  (let* ((normalized-text (normalize-text raw-text))
         (tokens (remove "" (split-sequence #\Space normalized-text) :test #'string=))
         (phrase-results (phrase-matches normalized-text))
         (phrase-canonicals (mapcar #'second phrase-results))
         (token-canonicals (token-matches tokens))
         (canonical-symptoms
           (dedupe-preserving-order (append phrase-canonicals token-canonicals))))
    (list
     :canonical-symptoms canonical-symptoms
     :matched-phrases phrase-results
     :unknown-terms (dedupe-preserving-order (unknown-terms tokens phrase-results)))))
