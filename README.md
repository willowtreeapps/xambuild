# xambuild
Build Xamarin projects outside of Visual Studio!

`xambuild` is a wrapper around `msbuild` and `nuget` that allows you to build Xamarin projects easily without an IDE.

## Installation
Just drop `xambuild.py` into the main directory of your project. If you want to place it elsewhere for organization reasons, see [Root Project Directory](#root-project-directory) configuration below. 

### Requirements
You will want to ensure you have Python >= 3.5 installed. Xambuild has been tested on MacOS but should work in other environments, including Windows.

## Setup
In many cases no additional setup is required. If you do need to modify a default, xambuild allows you to change configuration by both supplying arguments (1st priority) or through setting environment variables (2nd priority).

### Root Project Directory
Specifies the root project directory in relation to the invocation directory. The root project directory is the directory with a .sln file and \*.Droid and \*.iOS directories. 

The default value is `.`, for current directory. You can override this with the `XAMBUILD_PROJECT_DIR` environment variable or by supplying `-d <projectDir>` or `--projectDir <projectDir>`.

### Platform
Specifies the platform to build. Available options are `android` and `ios`.

The default value is `android`. You can override this with the `XAMBUILD_PLATFORM` environment variable or by supplying `-p <platform>` or `--platform <platform>`.

### Build Configuration
Specifies which build configuration to use. Examples include `Debug` and `Release`, though these will vary based on what is configured in your project's .csproj file. 

The default value is `Debug`. You can override this with the `XAMBUILD_CONFIGURATION` environment variable or by supplying `-c <platform>` or `--configuration <platform>`.

### Android Project Directory
This is the location of your android project directory with respect to your [Root Project Directory](#root-project-directory).

This defaults to the first (alphabetical) directory containing ".Droid" in the Root Project Directory. You can override this with the `XAMBUILD_DROID_DIR` environment variable or by supplying `-a <directory>` or `--droidDir <directory>`.

### iOS Project Directory
This is the location of your android project directory with respect to your [Root Project Directory](#root-project-directory).

This defaults to the first (alphabetical) directory containing ".iOS" in the Root Project Directory. You can override this with the `XAMBUILD_IOS_DIR` environment variable or by supplying `-i <directory>` or `--iosDir <directory>`.

## Running
Usage: `xambuild.py <flags> <command ...>`
`xambuild` offers the following commands:

* `buildAndDeploy` builds and deploys your app according to the specified options. For Android, this assumes you have one and only one device connected via ADB.
* `build` only compiles your project.
* `clean` cleans your project. Useful for when compilation fails for strange reasons.
* `updateAndroidResources` compiles only Android's resource files. Useful for quickly testing whether or not your XML changes are valid.
* `nuget` wraps the nuget executable, with the two following additions:
	* `wipe` wipes your nuget cache and all cached files. Using this in conjunction with the clean command fixes 99% of strange build issues, especially when changing nuget sources.
	* `restoreAll` restores the nuget packages for your project and all subprojects in one fell swoop. This is useful after fresh clones and wipes.
