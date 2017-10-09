import os
from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools
from conans.tools import os_info, SystemPackageTool, download, untargz, replace_in_file, unzip

class ConanRecipe(ConanFile):
    name = "portaudio"
    version = "v190600.20161030"
    settings = "os", "compiler", "build_type", "arch"
    FOLDER_NAME = "portaudio"
    description = "Conan package for the Portaudio library"
    url = "https://github.com/jgsogo/conan-portaudio"
    license = "http://www.portaudio.com/license.html"
    options = {"shared": [True, False], "fPIC": [True, False], "use_asio": [True, False]}
    default_options = "shared=False", "fPIC=True", "use_asio=True"
    exports_sources = ["FindPortaudio.cmake"]
    generators = "txt"

    WIN = {'build_dirname': "_build"}

    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def requirements(self):
        if self.options.use_asio:
            self.requires("AsioSDK/2.3@kenfred/testing")

    def system_requirements(self):
        if os_info.is_linux:
            if os_info.with_apt:
                installer = SystemPackageTool()
                installer.install("libasound2-dev")
                installer.install("libjack-dev")
            elif os_info.with_yum:
                installer = SystemPackageTool()
                installer.install("alsa-lib-devel")
                installer.install("jack-audio-connection-kit-devel")

    def source(self):
        zip_name = 'portaudio_%s' % self.version
        if self.version == 'master':
            self.run('mkdir portaudio')
            zip_name += '.zip'
            download('https://app.assembla.com/spaces/portaudio/git/source/master?_format=zip', 'portaudio/%s' % zip_name)
            unzip('portaudio/%s' % zip_name, 'portaudio/')
            os.unlink('portaudio/%s' % zip_name)
        else:
            zip_name += '.tgz'
            download('http://portaudio.com/archives/pa_stable_%s.tgz' % self.version.replace('.','_'), zip_name)
            untargz(zip_name)
            os.unlink(zip_name)

        if self.settings.os != "Windows":
            self.run("chmod +x ./%s/configure" % self.FOLDER_NAME)

    def build(self):
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            env = AutoToolsBuildEnvironment(self)
            with tools.environment_append(env.vars):
                env.fpic = self.options.fPIC
                with tools.environment_append(env.vars):
                    command = './configure && make'
                    self.run("cd %s && %s" % (self.FOLDER_NAME, command))
            if self.settings.os == "Macos" and self.options.shared:
                self.run('cd portaudio/lib/.libs && for filename in *.dylib; do install_name_tool -id $filename $filename; done')
        else:
            if self.settings.compiler == "gcc":
                replace_in_file(os.path.join(self.FOLDER_NAME, "CMakeLists.txt"), 'OPTION(PA_USE_WDMKS "Enable support for WDMKS" ON)', 'OPTION(PA_USE_WDMKS "Enable support for WDMKS" OFF)')
                replace_in_file(os.path.join(self.FOLDER_NAME, "CMakeLists.txt"), 'OPTION(PA_USE_WDMKS_DEVICE_INFO "Use WDM/KS API for device info" ON)', 'OPTION(PA_USE_WDMKS_DEVICE_INFO "Use WDM/KS API for device info" OFF)')
                replace_in_file(os.path.join(self.FOLDER_NAME, "CMakeLists.txt"), 'OPTION(PA_USE_WASAPI "Enable support for WASAPI" ON)', 'OPTION(PA_USE_WASAPI "Enable support for WASAPI" OFF)')

            build_dirname = self.WIN['build_dirname']

            cmake = CMake(self)

            if not os.path.exists(build_dirname):
                os.makedirs(build_dirname)

            defs = dict()
            defs['CMAKE_BUILD_TYPE'] = self.settings.build_type
            if self.options.use_asio:
                defs['ASIOSDK_PATH_HINT'] = "%s/ASIOSDK2.3" % self.deps_cpp_info["AsioSDK"].rootpath

            runtime_string = "%s" % self.settings.compiler.runtime
            if runtime_string[:2] == "MT":
                defs['PA_DLL_LINK_WITH_STATIC_RUNTIME'] = True
            else:
                defs['PA_DLL_LINK_WITH_STATIC_RUNTIME'] = False

            cmake.configure(source_dir="../%s" % self.FOLDER_NAME, build_dir=build_dirname, defs=defs)
            cmake.build()

    def package(self):
        self.copy("FindPortaudio.cmake", ".", ".")
        self.copy("portaudio/bindings/cpp/include/portaudiocpp/*", dst="include/portaudiocpp", keep_path=False)
        self.copy("portaudio/bindings/cpp/source/portaudiocpp/*", dst="source/portaudiocpp", keep_path=False)
        self.copy("*.h", dst="include", src=os.path.join(self.FOLDER_NAME, "include"))

        os_folder = "win" if self.settings.os == "Windows" else "unix"

        self.copy("*.h", src=os.path.join(self.FOLDER_NAME, "src", "os", os_folder), dst=os.path.join("include","os", os_folder), ignore_case=True, keep_path=False)

        self.copy(pattern="LICENSE*", dst="licenses", src=self.FOLDER_NAME, ignore_case=True, keep_path=False)

        cpp_bindings_path = os.path.join(self.FOLDER_NAME, "bindings", "cpp")
        cpp_bindings_src_path = os.path.join(cpp_bindings_path, "source", "portaudiocpp")
        cpp_bindings_include_path = os.path.join(cpp_bindings_path, "include", "portaudiocpp")
        self.copy(pattern="*.cxx", src=cpp_bindings_src_path, dst=os.path.join("bindings","cpp","src"), ignore_case=True, keep_path=False)
        self.copy(pattern="*.hxx", src=cpp_bindings_include_path, dst=os.path.join("include", "portaudiocpp"), ignore_case=True, keep_path=False)
        
        
        if self.settings.os == "Windows":
            build_dirname = self.WIN['build_dirname']
            if self.settings.compiler == "Visual Studio":
                self.copy("*.lib", dst="lib", src=os.path.join(build_dirname, str(self.settings.build_type)))
                if self.options.shared:
                    self.copy("*.dll", dst="bin", src=os.path.join(build_dirname, str(self.settings.build_type)))
            else:
                if self.options.shared:
                    self.copy(pattern="*.dll.a", dst="lib", keep_path=False)
                    self.copy(pattern="*.dll", dst="bin", keep_path=False)
                else:
                    self.copy(pattern="*static.a", dst="lib", keep_path=False)
                
        else:
            if self.options.shared:
                if self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", dst="lib", src=os.path.join(self.FOLDER_NAME, "lib", ".libs"))
                else:
                    self.copy(pattern="*.so*", dst="lib", src=os.path.join(self.FOLDER_NAME, "lib", ".libs"))
            else:
                self.copy("*.a", dst="lib", src=os.path.join(self.FOLDER_NAME, "lib", ".libs"))


    def package_info(self):
        base_name = "portaudio"
        if self.settings.os == "Windows":
            if not self.options.shared:
                base_name += "_static"
                
            if self.settings.compiler == "Visual Studio":
                base_name += "_x86" if self.settings.arch == "x86" else "_x64"
            
        elif self.settings.os == "Macos":
            self.cpp_info.exelinkflags.append("-framework CoreAudio -framework AudioToolbox -framework AudioUnit -framework CoreServices -framework Carbon")

        self.cpp_info.libs = [base_name]

        if self.settings.os == "Windows" and self.settings.compiler == "gcc" and not self.options.shared:
            self.cpp_info.libs.append('winmm')

        if self.settings.os == "Linux" and not self.options.shared:
            self.cpp_info.libs.append('jack asound m pthread')
