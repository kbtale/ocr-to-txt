import os
import sys

# Add the src directory to the path (insert at front to prefer local package)
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from main import main, process_image_file_cli


def _print_usage():
    print('Usage: run.py [--cli --input <file_or_dir> [--out <out_dir>]]')


def _process_folder(folder, out_dir=None):
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    for fname in os.listdir(folder):
        if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff')):
            inp = os.path.join(folder, fname)
            out_file = None
            if out_dir:
                base = os.path.splitext(fname)[0]
                out_file = os.path.join(out_dir, base + '.txt')
            process_image_file_cli(inp, out_file)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        main()
    else:
        if '--cli' in args:
            try:
                # parse minimal CLI args
                if '--input' in args:
                    i = args.index('--input') + 1
                    input_path = args[i]
                else:
                    _print_usage()
                    sys.exit(1)

                out_path = None
                if '--out' in args:
                    o = args.index('--out') + 1
                    out_path = args[o]

                if os.path.isdir(input_path):
                    _process_folder(input_path, out_path)
                else:
                    process_image_file_cli(input_path, out_path)
            except Exception as e:
                print('CLI processing failed:', e)
                sys.exit(2)
        else:
            _print_usage()
