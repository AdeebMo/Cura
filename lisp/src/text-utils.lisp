(defun sanitize-char (character)
  (if (or (alpha-char-p character) (digit-char-p character) (char= character #\Space))
      (char-downcase character)
      #\Space))

(defun split-sequence (delimiter text)
  (labels ((walk-parts (index current result)
             (cond
               ((>= index (length text))
                (nreverse (cons (coerce (nreverse current) 'string) result)))
               ((char= (char text index) delimiter)
                (walk-parts (1+ index) '() (cons (coerce (nreverse current) 'string) result)))
               (t
                (walk-parts (1+ index) (cons (char text index) current) result)))))
    (walk-parts 0 '() '())))

(defun normalize-text (text)
  (let* ((lowered
           (with-output-to-string (buffer)
             (loop for character across text do
               (cond
                 ((char= character #\')
                  nil)
                 ((or (alpha-char-p character)
                      (digit-char-p character)
                      (char= character #\Space))
                  (write-char (char-downcase character) buffer))
                 (t
                  (write-char #\Space buffer))))))
         (pieces (remove "" (split-sequence #\Space lowered) :test #'string=)))
    (format nil "~{~a~^ ~}" pieces)))

(defun dedupe-preserving-order (items)
  (labels ((walk-dedupe (remaining seen result)
             (if (null remaining)
                 (nreverse result)
                 (let ((item (car remaining)))
                   (if (member item seen :test #'string=)
                       (walk-dedupe (cdr remaining) seen result)
                       (walk-dedupe (cdr remaining) (cons item seen) (cons item result)))))))
    (walk-dedupe items '() '())))
