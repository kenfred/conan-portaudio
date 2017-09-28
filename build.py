
import os
from conan.packager import ConanMultiPackager
from conanfile import ConanRecipe


username = os.getenv("CONAN_USERNAME", "jgsogo")
reference = os.getenv("CONAN_REFERENCE", "{}/{}".format(ConanRecipe.name, ConanRecipe.version))


if __name__ == "__main__":
    builder = ConanMultiPackager(username=username,
                                 reference=reference,
                                 stable_branch_pattern="v190600.20161030"
                                )
    builder.add_common_builds(shared_option_name="portaudio:shared")
    filtered_builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        if settings["arch"] == "x86_64" and settings["build_type"] == "Release":
            filtered_builds.append([settings, options, env_vars, build_requires])
    builder.builds = filtered_builds

    print("{} builds ahead!".format(len(builder.builds)))
    builder.run()

