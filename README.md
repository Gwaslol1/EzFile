# EzFile
An easier and more abstracted file object for simple use cases in Python.

I've found that oftentimes when dealing with files in Python, I have to do one of a few things: run through the file and check it token by token; apply some change or function to the entirety of the file; strip certain parts of the file or only analyze certain parts of the file. The goal of EzFile is to just remove the boilerplate that always comes with those tasks. One simple example is the use of a sliding window to access tokens/lines in the file; this way the first task, running through the file and checking each token, is made trivial, with all of the boilerplate removed. Additionally, the user can supply a format to read the file in, so each token is dealt with as-is, without any conversion.


# Work in Progress

* Handling binary files
* Applying some function to the entire window
* Applying some function to the entire window
* Slicing lines read from the file according to some user-given formatting
