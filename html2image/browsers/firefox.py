from .browser import Browser
from .search_utils import find_firefox

import os
import shutil
import subprocess

class FirefoxHeadless(Browser):
    """
        Firefox browser wrapper.

        Parameters
        ----------
        - `executable` : str, optional
            + Path to a chrome executable.
        - `flags` : list of str
            + Flags to be used by the headless browser.
            + Default flags are :
                - '--default-background-color=00000000'
                - '--hide-scrollbars'
        - `print_command` : bool
            + Whether or not to print the command used to take a screenshot.
        - `disable_logging` : bool
            + Whether or not to disable Chrome's output.
    """

    def __init__(self, executable=None, flags=None, print_command=False, disable_logging=False,):
        self.executable = executable
        if not flags:
            self.flags = [
                '--default-background-color=00000000',
                '--hide-scrollbars',
            ]
        else:
            self.flags = [flags] if isinstance(flags, str) else flags

        self.print_command = print_command
        self.disable_logging = disable_logging

    def screenshot(
        self,
        input,
        output_path,
        output_file='screenshot.png',
        size=(1920, 1080),
    ):
        """ Calls Firefox headless to take a screenshot.

            Parameters
            ----------
            - `output_file`: str
                + Name as which the screenshot will be saved.
                + File extension (e.g. .png) has to be included.
                + Default is screenshot.png
            - `input`: str
                + File or url that will be screenshotted.
                + Cannot be None
            - `size`: (int, int), optional
                + Two values representing the window size of the headless
                + browser and by extention, the screenshot size.
                + These two values must be greater than 0.
            Raises
            ------
            - `ValueError`
                + If the value of `size` is incorrect.
                + If `input` is empty.
        """

        if not input:
            raise ValueError('The `input` parameter is empty.')

        if size[0] < 1 or size[1] < 1:
            raise ValueError(
                f'Could not screenshot "{output_file}" '
                f'with a size of {size}:\n'
                'A valid size consists of two integers greater than 0.'
            )

        output_path_file = os.path.join(output_path, output_file)
        command = [
            f'{self.executable}',
            '--headless',
            f'--window-size={size[0]},{size[1]}',
            *self.flags,
            '--screenshot',
            '-url',
            f'{input}',
        ]

        if self.print_command:
            print(' '.join(command))

        # If you try to screenshot with an output path (--screenshot [<path>])
        # in Firefox, for some reason it will not be saved.
        #
        # So we will save the screenshot with its default name ('screenshot.png')
        # in the temporary directory and then move it where it should be.

        # HACK: hardcoded temp dir
        # ideally we should somehow get access to the H2I instance's temp dir
        temp_dir = os.environ['TMP'] if os.name == 'nt' else '/tmp'
        temp_dir = os.path.join(temp_dir, 'html2image')

        subprocess.run(command, **self._subprocess_run_kwargs, cwd=temp_dir)
        shutil.move(os.path.join(temp_dir, 'screenshot.png'), output_path_file)


    @property
    def executable(self):
        return self._executable

    @executable.setter
    def executable(self, value):
        self._executable = find_firefox(value)

    @property
    def disable_logging(self):
        return self._disable_logging
    
    @disable_logging.setter
    def disable_logging(self, value):
        self._disable_logging = value

        # dict that will be passed unpacked as a parameter
        # to the subprocess.call() method to take a screenshot
        self._subprocess_run_kwargs = {
            'stdout': subprocess.DEVNULL,
            'stderr': subprocess.DEVNULL,
        } if value else {}
    
    def __enter__(self):
        print(
            'Context manager (with ... as:) is',
            f'not supported for {__class__.__name__}.'
        )

    def __exit__(self, *exc):
        pass
