Name:		kotlinx-coroutines-core-jvm
Version:	1.10.2
Release:	1
Summary:	Kotlin coroutines core for the JVM
Group:		Development/Java
License:	Apache-2.0
URL:		https://github.com/Kotlin/kotlinx.coroutines
# kotlinx-coroutines tag 1.10.2. JVM jar is common, concurrent, and jvm sources.
# The jar and sysjar index are versioned so kotlin-libs 1.6.4 can stay installed.
Source0:	kotlinx-coroutines-core-jvm-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-21-openjdk-devel
BuildRequires:	kotlin
BuildRequires:	sysjar
BuildRequires:	javapackages-filesystem
BuildRequires:	mvn(org.jetbrains.kotlin:kotlin-stdlib)
BuildRequires:	mvn(org.jetbrains.kotlinx:atomicfu-jvm)
BuildRequires:	mvn(org.codehaus.mojo:animal-sniffer-annotations)
BuildRequires:	mvn(com.google.android:annotations)

%description
org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm %{version}.
JVM coroutines from tag 1.10.2, compiled with the installed kotlinc 2.0.21
against atomicfu-jvm 0.26.1.

%prep
%autosetup -n kotlinx-coroutines-core-jvm-%{version}
find . -type f \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -print > binaries.list
if [ -s binaries.list ]; then
	cat binaries.list
	exit 1
fi

%build
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-21-openjdk
export PATH="$JAVA_HOME/bin:/usr/bin:/bin"
CPSTD=%{_javadir}/kotlin-stdlib.jar
ATOMIC=%{_javadir}/atomicfu-jvm.jar
SNIFF=%{_javadir}/animal-sniffer-annotations.jar
ANN=%{_javadir}/google-android-annotations.jar
test -s "$CPSTD"
test -s "$ATOMIC"
test -s "$SNIFF"
test -s "$ANN"
mkdir -p classes
find src/common -name '*.kt' | sort > common.list
printf '%s\n' src/concurrent/Builders.concurrent.kt src/concurrent/Dispatchers.kt src/concurrent/MultithreadedDispatchers.common.kt >> common.list
find src -name '*.kt' | sort > sources.list
test "$(wc -l < sources.list)" -eq 168
test "$(wc -l < common.list)" -eq 114
common=$(paste -sd, common.list)
kotlinc -J-Xmx2g -jvm-target 1.8 -language-version 2.0 -no-stdlib \
	-Xmulti-platform -Xexpect-actual-classes \
	-Xcommon-sources="$common" \
	-opt-in=kotlinx.coroutines.InternalCoroutinesApi \
	-opt-in=kotlin.experimental.ExperimentalTypeInference \
	-opt-in=kotlin.ExperimentalMultiplatform \
	-cp "$CPSTD:$ATOMIC:$SNIFF:$ANN" -d classes @sources.list
test -s classes/kotlinx/coroutines/BuildersKt.class
printf '%s\n' 'Manifest-Version: 1.0' 'Automatic-Module-Name: kotlinx.coroutines.core.jvm' > manifest.mf
jar cfm kotlinx-coroutines-core-jvm.jar manifest.mf -C classes .
jar i kotlinx-coroutines-core-jvm.jar
desc=$(jar --describe-module --file kotlinx-coroutines-core-jvm.jar)
printf '%s\n' "$desc"
if printf '%s\n' "$desc" | grep -F -q 'Unable'; then
	exit 1
fi
printf '%s\n' "$desc" | grep -F -qx 'kotlinx.coroutines.core.jvm automatic'
cat > kotlinx-coroutines-core-jvm.pom << END
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.jetbrains.kotlinx</groupId>
  <artifactId>kotlinx-coroutines-core-jvm</artifactId>
  <version>%{version}</version>
  <name>kotlinx-coroutines-core-jvm</name>
  <description>Kotlin coroutines core for the JVM</description>
  <url>https://github.com/Kotlin/kotlinx.coroutines</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.jetbrains.kotlin</groupId>
      <artifactId>kotlin-stdlib</artifactId>
      <version>2.0.21</version>
    </dependency>
    <dependency>
      <groupId>org.jetbrains.kotlinx</groupId>
      <artifactId>atomicfu-jvm</artifactId>
      <version>0.26.1</version>
    </dependency>
    <dependency>
      <groupId>org.codehaus.mojo</groupId>
      <artifactId>animal-sniffer-annotations</artifactId>
      <version>1.29</version>
    </dependency>
    <dependency>
      <groupId>com.google.android</groupId>
      <artifactId>annotations</artifactId>
      <version>4.1.1.4</version>
    </dependency>
  </dependencies>
</project>
END

%install
set -eo pipefail
sysjar install --buildroot %{buildroot} \
	--artifact kotlinx-coroutines-core-jvm.pom:kotlinx-coroutines-core-jvm.jar \
	--file-name kotlinx-coroutines-core-jvm-1.10.2 \
	--filelist .mfiles
idx="%{buildroot}/usr/share/sysjar/index/org.jetbrains.kotlinx/kotlinx-coroutines-core-jvm.sysjar"
/bin/mv "$idx" "%{buildroot}/usr/share/sysjar/index/org.jetbrains.kotlinx/kotlinx-coroutines-core-jvm-1.10.2.sysjar"
sed -i 's|kotlinx-coroutines-core-jvm\.sysjar|kotlinx-coroutines-core-jvm-1.10.2.sysjar|' .mfiles
idx="%{buildroot}/usr/share/sysjar/index/org.jetbrains.kotlinx/kotlinx-coroutines-core-jvm-1.10.2.sysjar"
test -s "$idx"
grep -F -q '"version": "%{version}"' "$idx"
grep -F -q '"artifactId": "kotlinx-coroutines-core-jvm"' "$idx"
grep -F -q '/usr/share/java/kotlinx-coroutines-core-jvm-1.10.2.jar' "$idx"
test -s %{buildroot}%{_javadir}/kotlinx-coroutines-core-jvm-1.10.2.jar
if [ -e %{buildroot}%{_javadir}/kotlinx-coroutines-core-jvm.jar ]; then
	exit 1
fi

%check
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-21-openjdk
export PATH="$JAVA_HOME/bin:/usr/bin:/bin"
JAR=%{buildroot}%{_javadir}/kotlinx-coroutines-core-jvm-1.10.2.jar
test -s "$JAR"
STDLIB=%{_javadir}/kotlin-stdlib.jar
ATOMIC=%{_javadir}/atomicfu-jvm.jar
mkdir -p check
cat > check/Probe.kt << 'EOF'
import kotlinx.atomicfu.atomic
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking

fun main() {
    val result = runBlocking {
        val counter = atomic(41)
        delay(1)
        counter.incrementAndGet()
    }
    if (result != 42) error("coro")
    println("kotlinx_coroutines_ok " + result)
}
EOF
kotlinc -J-Xmx1g -jvm-target 1.8 -language-version 2.0 \
	-cp "$JAR:$ATOMIC:$STDLIB" -d check/out check/Probe.kt
java -cp "check/out:$JAR:$ATOMIC:$STDLIB" ProbeKt > check/out.txt
cat check/out.txt
grep -F -qx 'kotlinx_coroutines_ok 42' check/out.txt

%files -f .mfiles
%license LICENSE.txt
