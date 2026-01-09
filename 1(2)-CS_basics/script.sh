
# anaconda(또는 miniconda)가 존재하지 않을 경우 설치해주세요!
## TODO
if ! command -v conda &> /dev/null; then
    echo "[INFO] Conda가 설치되어 있지 않습니다. Miniconda 설치를 시작합니다."
    mkdir -p ~/miniconda3
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
    bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
    rm -rf ~/miniconda3/miniconda.sh
    source ~/miniconda3/bin/activate
    conda init bash
else
    echo "[INFO] Conda가 이미 설치되어 있습니다."
    # 쉘 설정에 따라 conda 명령어가 바로 안 먹힐 수 있으므로 source 시도
    source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || source $(conda info --base)/etc/profile.d/conda.sh
fi


# Conda 환셩 생성 및 활성화
## TODO
if ! conda info --envs | grep -q "myenv"; then
    echo "[INFO] 'myenv' 가상환경을 생성합니다."
    conda create -n myenv python=3.10 -y
fi
conda activate myenv

## 건드리지 마세요! ##
python_env=$(python -c "import sys; print(sys.prefix)")
if [[ "$python_env" == *"/envs/myenv"* ]]; then
    echo "[INFO] 가상환경 활성화: 성공"
else
    echo "[INFO] 가상환경 활성화: 실패"
    exit 1 
fi

# 필요한 패키지 설치
## TODO
pip install mypy

# Submission 폴더 파일 실행
cd submission || { echo "[INFO] submission 디렉토리로 이동 실패"; exit 1; }

for file in *.py; do
    ## TODO
    filename="${file%.py}"  # 확장자(.py) 제거한 파일명 추출 (예: 2243)
    
    # 입력 파일: ../input/{문제번호}_input
    # 출력 파일: ../output/{문제번호}_output
    # (이미 submission 폴더로 들어왔으므로 상위 폴더(..)로 나가야 함)
    problem_num="${filename#*_}" 
    input_file="../input/${problem_num}_input"
    output_file="../output/${problem_num}_output"

    if [ -f "$input_file" ]; then
        python "$file" < "$input_file" > "$output_file"
        echo "[INFO] 실행 완료: $file -> $output_file"
    else
        echo "[WARN] 입력 파일이 존재하지 않습니다: $input_file (원본: $file)"
    fi
done

# mypy 테스트 실행 및 mypy_log.txt 저장
## TODO
echo "[INFO] mypy 테스트를 수행합니다..."
# 현재 디렉토리(submission) 내의 모든 파일 검사 후 상위 폴더에 로그 저장
mypy . > ../mypy_log.txt


# conda.yml 파일 생성
## TODO
echo "[INFO] conda 환경 정보를 저장합니다..."
conda env export > ../conda.yml

# 가상환경 비활성화
## TODO
conda deactivate
echo "[INFO] 가상환경이 비활성화되었습니다."
