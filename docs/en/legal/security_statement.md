# Security Statement

## System Security Hardening

It is recommended that users enable ASLR (Level 2), also known as **full Address Space Layout Randomization**, in the system. This can be configured as follows:

    echo 2 > /proc/sys/kernel/randomize_va_space

## Operating User Recommendations

1. The tools in this code repository are designed for installation and use with low privileges. From the perspective of security and the principle of least privilege, none of the tools should be used with high-privilege accounts such as root. It is recommended to install and execute them with standard user permissions.

2. If a tool depends on CANN, for security purposes, use the CANN package installed by default under the same low-privilege user. After executing `source`, do not arbitrarily modify the environment variables involved in `set_env.sh`.

3. Before using any tool in this code repository, it is recommended to set `umask` to `0027` or higher to ensure that generated files meet the minimum privilege security requirements.

4. This tool is a development-phase tool. It does not restrict the installation owner and permissions, nor does it restrict the owner and permissions of the file objects processed by the tool. Users must assign appropriate ownership and permissions based on the usage scenario and ensure that the file content processed by the tool is secure and trustworthy.

5. When providing input to the tool, users must ensure the content is secure and trustworthy, avoid symbolic links, and convert all files to their real absolute paths before inputting them into the tool.

## File Access Control

 1. When users provide input files to the tool, it is recommended that the file owner be consistent with the tool process owner, and the file permissions should not be modifiable by others (including group and others). By default, files written to disk by the tool are not writable by users in the same group or other users. Users can control permissions on the generated files as needed.

 2. Users need to properly control permissions during installation and usage. It is recommended to configure settings by referring to the file permission reference.

## File Access Control

| Type                               | Maximum Linux Permission Reference |
| ---------------------------------- | ---------------------------------- |
| User Home Directory                | 750 (rwxr-x---)                    |
| Program Files (including script files, library files, etc.) | 550 (r-xr-x---)                    |
| Program File Directory             | 550 (r-xr-x---)                    |
| Configuration Files                | 640 (rw-r-----)                    |
| Configuration File Directory       | 750 (rwxr-x---)                    |
| Log Files (completed or archived)  | 440 (r--r-----)                    |
| Log Files (currently recording)    | 640 (rw-r-----)                    |
| Log File Directory                 | 750 (rwxr-x---)                    |
| Debug Files                        | 640 (rw-r-----)                    |
| Debug File Directory               | 750 (rwxr-x---)                    |
| Temporary File Directory           | 750 (rwxr-x---)                    |
| Maintenance and Upgrade File Directory | 770 (rwxrwx---)                    |
| Business Data Files                | 640 (rw-r-----)                    |
| Business Data File Directory       | 750 (rwxr-x---)                    |
| Key Components, Private Keys, Certificates, Ciphertext File Directory | 700 (rwx------)                    |
| Key Components, Private Keys, Certificates, Encrypted Ciphertext | 600 (rw-------)                    |
| Encryption/Decryption Interfaces, Encryption/Decryption Scripts | 500 (r-x------)                    |

## Vulnerability Security Statement

Please refer to the [MindStudio Vulnerability Handling Procedure](./vulnerability_handling_procedure.md).

## Data Security

During tool usage, some code-line-related functions will access customer operator code. If the operator code is confidential and must not be disclosed, please delete the corresponding deliverables promptly after use to prevent unnecessary information leakage.

## Build Security

This project supports source code compilation and installation. During compilation, dependent third-party libraries are downloaded and build shell scripts are executed. Temporary program files and compilation directories are generated during the build process. Users may implement File Access Control on files within the source code directory as needed to reduce security risks. During the build process, users may modify build scripts as necessary to avoid related security risks, and should pay attention to the security of the build results.

## Runtime Security

1. When an exception occurs during runtime, the tool will exit the process and print an error message, which is normal behavior. Users are advised to locate the specific cause of the error based on the error prompts, including methods such as viewing Log Files and collecting result files generated during the parsing process.

2. During tool usage, no security validation is performed on user input programs. Users are responsible for ensuring the security of their programs themselves.

## Public Network Addresses

The tool does not involve the use of public IP addresses.

## Public APIs

This project is developed in Python and the source code is released. It is recommended to directly use the public interfaces described in the documentation. Directly calling the source code of interfaces that are not explicitly made public is not recommended.

## Secure Function Usage Instructions

Insecure functions are not forcibly disabled, but it is recommended to use the _s secure versions that explicitly pass the buffer length as a parameter, such as memset_s, memcpy_s, etc.

## Communication Security Hardening

Remote communication is not involved at this time. It is recommended that users use the tool within a secure network environment protected by a firewall or a local area network, and pay attention to the communication security of other third-party software.

## Communication Matrix

External port communication is not involved at this time.
