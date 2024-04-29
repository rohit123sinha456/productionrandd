import subprocess
nssm_path = r'D:\Rohit\nssm\win64\nssm.exe'  # Path to NSSM executable

def create_copy_of_pyfile(original_file,new_file):
    try:
        with open(original_file, 'rb') as original:
            with open(new_file, 'wb') as new:
                new.write(original.read())
        print(f"File '{original_file}' duplicated as '{new_file}' successfully.")
    except FileNotFoundError:
        print(f"Error: File '{original_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def edit_python_file(file_path, old_content, new_content):
    try:
        # Read the content of the file
        with open(file_path, 'r') as file:
            file_content = file.read()

        # Replace the old content with the new content
        modified_content = file_content.replace(old_content, new_content)

        # Write the modified content back to the file
        with open(file_path, 'w') as file:
            file.write(modified_content)

        print(f"File '{file_path}' edited successfully.")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def create_nssm_service(service_name, executable_path, args, display_name, appdir):
    global nssm_path

    # Construct the command to create the service
    install_command = [nssm_path, 'install', service_name, executable_path,args]
    set_appdir_command = [nssm_path, 'SET', service_name,'AppDirectory', appdir]
    set_display_command = [nssm_path, 'SET', service_name,'DisplayName', display_name]
    remove_command =  [nssm_path,'remove', service_name,'confirm']
    try:
        subprocess.run(install_command, shell=True)
        subprocess.run(set_display_command, shell=True)
        subprocess.run(set_appdir_command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f'Error: {e}')
        subprocess.run(remove_command, shell=True)
        return
    print("Successfully Created Services")


if __name__=="__main__":
    old_file_path = 'dummy.py'
    old_content = '192.168.1.1'  
    new_file_paths = ['newdummy1.py','newdummy2.py','newdummy3.py']
    new_contents = ['192.168.1.102','192.168.1.201','192.168.1.303']
    for i,new_file_path in enumerate(new_file_paths):
        create_copy_of_pyfile(old_file_path,new_file_path)
        edit_python_file(new_file_path, old_content, new_contents[i])
        camera_extension = new_contents[i].split(".")[-1]
        create_nssm_service(
            service_name=f'SudisaAI{camera_extension}',
            executable_path=r'D:\Rohit\Sudisa\safety\productionrandd\env\Scripts\python.exe',
            args=new_file_path,
            appdir=r'D:\Rohit\Sudisa\safety\CD',
            display_name=f"SudisaAI{camera_extension}")
