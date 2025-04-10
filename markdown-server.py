'''Simple Markdown File Rendering Webserver'''

import argparse, logging, os, sys, re

from nicegui import ui
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def main(markdown_file: Path):
    ''' START '''
    date_today_str = datetime.now().strftime("%Y-%m-%d")
    logger.info("Starting Markdown Server: " + str(date_today_str))
    
    ''' title of page '''
    ui.page_title('Markdown Server')

    ''' create a list of dicts that contain infomation about the content in the markdown file'''
    renderableItems = split_markdown_by_mermaid_blocks(markdown_file)

    '''for each item in the list, decide if the content is text or a mermaid chart, and render accodingly to nicegui ui'''
    for item in renderableItems:
        if item['type'] == "text":
            ui.markdown(item['content'])
        elif item['type'] == "mermaid":
            ui.mermaid(item['content']).style('width: 100%; height: 100%;')
                     
    ''' run server, reload when files are modified '''
    ui.run(show=False)
    

def split_markdown_by_mermaid_blocks(markdown_file: Path):
    ''' 
    takes a file path in to a markdown file, determines where mermaid diagrams are emedded
    returns a list of dicts such:
    {'type': 'text', 'content': '# Example Markdown\n\nThis is some text before the mermaid chart.'}
    {'type': 'mermaid', 'content': 'graph TD;\n    A-->B;\n    A-->C;\n    B-->D;\n    C-->D;'}
    ''' 

    with open(markdown_file, 'r') as readme_in:
        markdown_content = readme_in.read() # save to var

    # Regular expression to match mermaid blocks
    mermaid_pattern = r"``` mermaid(.*?)```"
    
    # Find all mermaid blocks using re.DOTALL to match across multiple lines
    mermaid_blocks = re.findall(mermaid_pattern, markdown_content, re.DOTALL)
    
    # Split the markdown content into parts excluding the mermaid blocks
    non_mermaid_parts = re.split(mermaid_pattern, markdown_content, flags=re.DOTALL)
    
    # Combine the results into a list of objects
    result = []
    for i, part in enumerate(non_mermaid_parts):
        if i % 2 == 0:  # Non-mermaid content
            result.append({"type": "text", "content": part.strip()})
        else:  # Mermaid block
            result.append({"type": "mermaid", "content": part.strip()})
    
    return result
                
def set_up_logging(packages, log_level, log_file):
    '''Set up logging for specific packages/modules.'''
    formatter = logging.Formatter('%(asctime)s - %(process)d - %(levelname)s - %(message)s')
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    for package in packages:
        package_logger = logging.getLogger(package)
        package_logger.addHandler(stream_handler)
        package_logger.addHandler(file_handler)
        package_logger.setLevel(log_level)
  
def parse_args():
    '''Parse command line arguments.'''
    parser = argparse.ArgumentParser()

    # Command line arguments for input.
    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--markdown-file",type=Path,required=True,help="Path to markdown file to be rendered")

    # Command line arguments for logging configuration.
    logging_group = parser.add_argument_group('Logging')
    log_choices = ['DEBUG', 'CRITICAL', 'FATAL', 'ERROR', 'WARNING', 'WARN', 'INFO', 'NOTSET']
    logging_group.add_argument(
        '--log-level',
        required=False,
        default='INFO',
        metavar='LEVEL',
        type=str.upper, # nice trick to catch ERROR, error, Error, etc.
        choices=log_choices,
        help=f'log level {log_choices}'
    )
    logging_group.add_argument("--log-file-path",required=False,default=Path("./logs/"),type=Path,help="log file path. (deafult is cwd)")
    
    return parser.parse_args()


if __name__ in {"__main__", "__mp_main__"}: #to allow server to run within mp
    try:
        ''' parse args '''
        args = parse_args()
        print(args)
        
        ''' create log dir if doesn't already exist '''
        os.makedirs(args.log_file_path, exist_ok=True)
        
        ''' set up logging, add packages (class files that need to be included for logging) '''
        set_up_logging(
            packages=[
                __name__, # always
            ],
            log_level=args.log_level,
            log_file=Path(args.log_file_path / Path(f'{datetime.today().year}-{str(datetime.today().month).zfill(2)}-server.log'))
        )
        
        ''' run main '''
        main(args.markdown_file)
    except Exception as e:
        logger.error(f'Unknown exception of type: {type(e)} - {e}')
        raise e
