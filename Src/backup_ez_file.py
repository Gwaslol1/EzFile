from __future__ import annotations, print_function
from typing import Iterator, Generator
from traceback import print_tb

__all__ = ["EzFile"]


class EzFile:
    """An easier and more abstracted file object."""
    def __init__(
            self, file_path: str, mode: str, filtr: str=None, delimit: str=None, 
            window_size: int=0, chunk_size: int=0, keep_nl: bool=False, 
            DEBUG: bool=False) -> None:
        self._file_path = file_path
        self._file_mode = mode
        self._filter = filtr
        self._delimit = delimit
        self._window_size = window_size
        self._chunk_size = chunk_size
        self._keep_nl = keep_nl
        self._DEBUG = DEBUG

        # Setup
        self._file = None
        self._binary = True if 'b' in mode else False
        self._window_buffer = [] if self._window_size else None
        self._relative_middle = int(self._window_size / 2) if self._window_size else None # -> Python floors on int cast
        self._current_chunk = 0 # -> chunk defaults to one line in text mode, user defined in binary mode
        
        # Exception handling
        if self._binary and not chunk_size: raise ValueError("Could not enable binary - chunk_size must be specified in binary mode.")
        if self._window_size <= 1: raise ValueError("Could not initialize window - window size must be greater than 1.")
        elif self._window_size % 2 == 0: self._window_size += 1 # -> silently change an even window with no middle

    def __name__(self) -> str:
        """Returns a string reprsentation of EzFile."""
        return f"{self.__class__.__name__}"

    def __repr__(self) -> str:
        """Returns a string representation of EzFile."""
        return f"{self.__class__.__name__}({self._file_path}, {self._file_mode}, {str(self._filter)})"

    def __str__(self) -> str:
        """Returns a string representation of EzFile."""
        return f"{self.__class__.__name__}({self._file_path}, {self._file_mode}, {str(self._filter)})"

    def __enter__(self) -> EzFile:
        """Enters context and propagates exception if present; returns the class instance after loading the file."""
        try:
            self._file = open(self._file_path, self._file_mode)
        except OSError:
            raise ValueError("Could not open file - file with specified path does not exist.")
        return self

    def __exit__(self, exc_type: Exception, exc_value: Exception, trace: object) -> bool:
        """Exits context and propagates exception if present; releases file resources."""
        self._close_file()
        if exc_type:
            print(f"\nException occurred - [{type.__name__}]") if self._DEBUG else 0
            print_tb(trace) if self._DEBUG else 0
            return True

    def __bool__(self) -> bool:
        """Returns the truth value of the file based on whether the current element exists."""
        return self._window_buffer[self._relative_middle] is not None

    def __iter__(self) -> Iterator[EzFile]:
        """Returns an iterator to the file contents."""
        if self._file is None:
            raise ValueError("Could not generate file iterator - no file loaded.")
        return self._create_generator()

    def __getitem__(self, index: int) -> str:
        """Returns the buffered chunk read from file if it exists."""
        try:
            # UNDERSTANDABLE WAY
            # absolute_middle = (self._current_chunk - 1) - self._relative_middle
            # relative_index = self._relative_middle + (index - absolute_middle)
            relative_index = self._relative_middle + (index - (self._current_chunk - 1 - self._relative_middle))
            if relative_index < 0 or relative_index >= self._window_size: raise IndexError
            return self._window_buffer[relative_index]
        except TypeError:
            raise TypeError("Could not access data window - index is not an integer.")
        except IndexError:
            raise IndexError("Could not access data window - index is out of range.")

    def __del__(self) -> None:
        """Releases file resources."""
        self._close_file()

    def _close_file(self) -> None:
        """Closes the currently loaded file."""
        if self._file:
            self._file.close()
            self._file = None

    def _format_line(self, line: str) -> str: # TODO
        """Formats a line according to the current filter."""
        return

    def _read_line(self) -> str:
        """Reads a line from the file."""
        line = (self._file.readline()).strip("\n") if not self._keep_nl else self._file.readline()
        self._current_chunk += 1
        print(f"Line - [{line}] : Current Chunk - [{self._current_chunk}]")
        if not line: return None
        elif self._filter: return self._format_line(line)
        else: return line

    def _init_window_buffer(self) -> None:
        """Sets up the initial window state."""
        # TODO -> Add binary functionality
        for i in range(self._window_size):
            if i < self._relative_middle: self._window_buffer.append(None)
            else: self._window_buffer.append(self._read_line())

    def _update_window_buffer(self) -> None:
        """Stores the given line in memory, removing the oldest line."""
        self._window_buffer.pop(0)
        self._window_buffer.append(self._read_line())

    def _create_generator(self) -> Generator[str]:
        """Returns a generator associated with the currently loaded file object."""
        # TODO -> Add binary functionality
        if not self._window_size: return iter(self._file) # TODO -> This should deal with newlines, not necessarily just return iter(file)
        print(f"Window buffer - {self._window_buffer}") if self._DEBUG else 0
        while True:
            self._update_window_buffer() if self._window_buffer else self._init_window_buffer()
            if not self._window_size: break
            elif self._window_buffer[self._relative_middle] is None: break
            yield self._window_buffer[self._relative_middle]

    def load_file(self) -> None: # TODO -> Should this return the file object or leave it abstracted? They can always just make one themselves...
        """Loads a file object into memory based on the given file path and mode."""
        try:
            self._file = open(self._file_path, self._file_mode)
        except OSError:
            raise ValueError("Could not open file - file with specified path does not exist.")

    def set_filter(self, filtr: str) -> None:
        """Set filter."""
        self._filter = filtr

    def get_window(self) -> list[str]:
        """Returns the window: does not guarantee size of list returned to be the max window size."""
        if not self._window_size: raise ValueError("Could not access data window - window not initialized.")
        return list(filter(lambda x : x is not None, self._window_buffer))

    def get_chunk(self, index: int) -> str:
        """Gets a chunk of data from the window given the index. Index is relative to current chunk, not start of window."""
        try:
            # TODO -> Maybe enforce the index being relative to the middle, idk how tho
            return self._window_buffer[self._relative_middle + (index - self._relative_middle)]
        except TypeError:
            raise TypeError("Could not access data window - index is not an integer.")
        except IndexError:
            raise IndexError("Could not access data window - index is out of range.")

    def read_chunk(self) -> str:
        """Returns a chunk of data from the file, defaults to one line in text mode, user defined in binary mode."""
        # TODO -> Add binary functionality
        if not self._window_size: return self._read_line()
        if not self._window_buffer: self._init_window_buffer() # TODO -> How to handle buffer indices after user calls this method?
        else: self._update_window_buffer()
        return self._window_buffer[self._relative_middle]

    def apply_to_window(self, callback: function) -> bool: # TODO
        """Applies the callback function to the current window. Requires a full window."""
        return

    def apply_to_file(self, callback: function) -> bool: # TODO
        """Applies the callback function to every line in the file."""
        return


def main() -> None:
    print(f"\nStarting {EzFile.__name__}:{__name__}...\n")
    file_path = "test.txt"
    try:
        with EzFile(file_path, "r", window_size=5) as efile:
            try:
                for index, line in enumerate(efile):
                    # print(f"Current line - [{line}] : Previous line - [{efile[index - 1]}]")
                    test = efile[index - 1]
                    print(f"Test - [{test}]")
                    # accessed = map(lambda x : str(x).upper() if efile[index - 1] == x else x, efile._window_buffer)
                    # print(f"Idx: {index - 1} - [{list(accessed)}]")

            except Exception as e:
                print(e)
                print_tb()
    except Exception as e:
        print(e)
        print_tb()


if __name__ == "__main__":
    main()
