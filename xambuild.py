#!/usr/bin/env python3

# Requires Python >= 3.5

# Goals: This script aspires to be a standalone replacement
# for Visual Studio Mac for Xamarin.Android development.
# The user interface should require as little setup as
# possible and should be guided.

# Functions supported: build, clean, deploy, update android resources, android sign, view environment variable config state,
# nuget wipe/restoreAll/* (this script wraps nuget to add wipe and restoreAll)

# Optional environment variables:
## XAMBUILD_PROJECT_DIR- Root project directory. Defaults to '.'
## XAMBUILD_DROID_DIR- Android project directory. Defaults to the first (alphabetically) directory containing "Droid" in XAMBUILD_PROJECT_DIR
## XAMBUILD_IOS_DIR- iOS project directory. Defaults to the first (alphabetically) directory containing "iOS" in XAMBUILD_PROJECT_DIR
## XAMBUILD_PLATFORM- Default build platform if one is not specified in invocation flags. Default value is "android".
## XAMBUILD_CONFIGURATION- Default build configuration if one is not specified in invocation flags. Default value is "Debug".

# Error codes:
## 0: Success.
## 1: Cancelled by keyboard interrupt.
## 2: Error parsing platform. Check XAMBUILD_PLATFORM and/or the --platform argument, if provided.
## 3: Error finding platform-specific .csproj file. 
## 4: Unable to find platform-specific folders in the project directory.
## 5: No action or bad action supplied.
## Others: If msbuild or nuget emit a nonzero error code, xambuild will have its error code equal the wrapped program's error code.
## All xambuild errors emit a message to standard out along with the error codes shown above.

import argparse, glob, os, subprocess, sys

# Variable defaults

def projectDirDefault():
    projectDirEnv = os.environ.get('XAMBUILD_PROJECT_DIR') or os.path.realpath(".")
    return projectDirEnv

def droidDirDefault(args):
        try:
            projectDirEnv = os.environ.get('XAMBUILD_DROID_DIR') or os.path.realpath(glob.glob(args.projectDir + os.sep + "*.Droid")[0])
            return projectDirEnv
        except:
            print("Platform directory could not be found, exiting.")
            SystemExit(4)

def iosDirDefault(args):
        try:
            projectDirEnv = os.environ.get('XAMBUILD_IOS_DIR') or os.path.realpath(args.projectDir + os.sep + glob.glob("*.iOS")[0])
            return projectDirEnv
        except IndexError:
            print("Platform directory could not be found, exiting.")
            SystemExit(4)

def platformDefault():
    platformEnv = os.environ.get('XAMBUILD_PLATFORM') or "android"
    return platformEnv.lower()

def buildConfigurationDefault():
    config = os.environ.get('XAMBUILD_CONFIGURATION') or "Debug"
    return config

# Helper functions

def platformDir(args):
    if args.platform == 'android':
        return args.droidDir
    elif args.platform == 'ios':
        return args.iosDir
    else:
        print("Error parsing platform. Check XAMBUILD_PLATFORM and the --platform argument.", file=sys.stderr)
        SystemExit(2)

def platformCsproj(args):
    try:
        csproj = glob.glob(platformDir(args) + os.sep + "*.csproj")[0]
        return csproj
    except IndexError:
        print("Error finding platform-specific csproj file. Check to see that your platform directory is correct.")
        SystemExit(3)


def buildConfigurationString(args):
    return "/p:Configuration="+args.buildConfiguration

def safeRun(toRun):
    try:
        if toRun:
            print("=> " + " ".join(toRun))
            retcode = subprocess.run(toRun).returncode
            return retcode
        else:
            print("Error: Asked to run program ''.")
    except KeyboardInterrupt:
        print("Cancelled by keyboard interrupt.")
        SystemExit(1)
    except Exception as ex:
        print("Error in called program " + toRun.index(0) + ": " + str(ex))

# Script commands

def default(args):
    if len(args.action) == 0:
        print("No action given. Try ./xambuild.ph -h for help.")
    else:
        print("Invalid action '" + args.action[0] + "'. Try ./xambuild.py -h for help.")
    return 5

def nuget(args):
    if len(args.action) > 0 and args.action[0] == "restoreAll":
        nugetRestore(args)
    elif len(args.action) > 0 and args.action[0] == "wipe":
        nugetWipe(args)
    else:
        safeRun(["nuget"] + args.action)

def nugetWipe(args):
    print("Wiping nuget...")
    safeRun(["nuget", "locals", "all", "-clear"])
    projects = glob.glob(args.projectDir + os.sep + '*' + os.sep, recursive=True)
    if not projects:
        print("No project folders found in the project directory. Check XAMBUILD_PROJECT_DIR")
        SystemExit(4)
    for project in projects:
        #only run on this directory if a csproj file is present
        if glob.glob(project + '*.csproj'):
            safeRun(["rm", "-rf", project + "bin"])
            safeRun(["rm", "-rf", project + "obj"])

def nugetRestore(args):
    print("Restoring nuget...")
    projects = glob.glob(args.projectDir + os.sep + '*' + os.sep + '*.csproj', recursive=True)
    if not projects:
        print("No project folders found in the project directory. Check XAMBUILD_PROJECT_DIR.")
        SystemExit(4)
    for project in projects:
        safeRun(["nuget", "restore", project])

def buildAndDeploy(args):
    print("Building and deploying " +  args.buildConfiguration + " configuration...")
    return safeRun(["msbuild", platformCsproj(args), buildConfigurationString(args), "/t:Install"])

def build(args):
    print("Building " +  args.buildConfiguration + " configuration...")
    return safeRun(["msbuild", platformCsproj(args), buildConfigurationString(args)])

def listEnvVars(args):
    print("XAMBUILD_PROJECT_DIR:", os.environ.get('XAMBUILD_PROJECT_DIR') or "not set")
    print("XAMBUILD_DROID_DIR:", os.environ.get('XAMBUILD_DROID_DIR') or "not set")
    print("XAMBUILD_IOS_DIR:", os.environ.get('XAMBUILD_IOS_DIR') or "not set")
    print("XAMBUILD_PLATFORM:", os.environ.get('XAMBUILD_PLATFORM') or "not set")
    print("XAMBUILD_CONFIGURATION:", os.environ.get('XAMBUILD_CONFIGURATION') or "not set")
    return 0

def androidSign(args):
    print("Building and signing " +  args.buildConfiguration + " configuration...")
    return safeRun(["msbuild", platformCsproj(args), buildConfigurationString(args), "/t:SignAndroidPackage"])

def clean(args):
    print("Running a project clean...")
    return safeRun(["msbuild", platformCsproj(args), buildConfigurationString(args), "/t:Clean"])

def updateAndroidResources(args):
    print("Updating android resources...")
    return safeRun(["msbuild", platformCsproj(args), buildConfigurationString(args), "/t:UpdateAndroidResources"])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Builds and mantains Xamarin projects outside of Visual Studio by calling msbuild/nuget directly.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-p", "--platform", dest="platform", default=platformDefault(), help="specify platform to compile.\n    *Default is XAMBUILD_PLATFORM or 'android'\n    *Expects one of 'android' or 'ios'.", type=str)
    parser.add_argument("-d", "--projectDir", dest="projectDir", default=projectDirDefault(), help="xamarin project root directory.\n    *Default is '.'", type=str)
    parser.add_argument("-c", "--configuration", dest="buildConfiguration", default=buildConfigurationDefault(), help="Set build configuration. \n    *Default is 'Debug'", type=str)
    parser.add_argument("-a", "--droidDir", dest="droidDir", help="xamarin.android project root directory.\nDefault is first directory containing 'Droid' in projectDir.", type=str)
    parser.add_argument("-i", "--iosDir", dest="iosDir", help="xamarin.iOS project root directory.\nDefault is first directory containing 'iOS' in projectDir.", type=str)
    parser.add_argument("action", type=str, nargs='+', help="actions are buildAndDeploy, clean, updateAndroidResources, and nuget <wipe, restoreAll, *>")
    args = parser.parse_args()

    if not args.iosDir:
        args.iosDir = iosDirDefault(args)

    if not args.droidDir:
        args.droidDir = droidDirDefault(args)

    choices = { 'default': default, 'buildAndDeploy': buildAndDeploy, 'build': build, 'clean': clean, 'updateAndroidResources': updateAndroidResources, 'nuget': nuget, 'listEnvVars': listEnvVars, 'androidSign': androidSign }
    if (args.action[0] in choices):
        errcode = choices.get(args.action.pop(0), default)(args)
    else:
        errcode = default(args)
    print("Done!")
    if errcode:
        SystemExit(errcode)
    else:
        SystemExit(0)