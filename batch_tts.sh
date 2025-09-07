#!/bin/bash

# 安全批量处理启动脚本
# 包含多种预设配置，适用于不同规模的文件处理

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 检查虚拟环境
check_venv() {
    if [[ "$VIRTUAL_ENV" != *"venv-tts"* ]]; then
        print_warning "检测到未激活TTS虚拟环境"
        print_info "正在激活虚拟环境..."
        source ~/venv-tts/bin/activate
        if [ $? -eq 0 ]; then
            print_success "虚拟环境激活成功"
        else
            print_error "虚拟环境激活失败，请手动执行: source ~/venv-tts/bin/activate"
            exit 1
        fi
    else
        print_success "TTS虚拟环境已激活"
    fi
}

# 显示使用帮助
show_help() {
    echo "安全批量TTS处理脚本"
    echo ""
    echo "使用方法:"
    echo "  $0 <模式> <输入文件> <输出目录> [--skip-existing]"
    echo ""
    echo "模式选项:"
    echo "  conservative  - 保守模式: 每批2-3个问题，间隔10-20分钟 (推荐用于大文件)"
    echo "  balanced     - 平衡模式: 每批3-5个问题，间隔5-15分钟  (默认模式)"
    echo "  aggressive   - 激进模式: 每批5-8个问题，间隔2-8分钟   (小文件快速处理)"
    echo "  test         - 测试模式: 每批1个问题，间隔0.5-1分钟  (调试用)"
    echo "  custom       - 自定义模式: 需要额外参数 <批次大小> <间隔时间>"
    echo ""
    echo "可选参数:"
    echo "  --skip-existing  - 跳过已经转换成功的题目，加速增量处理"
    echo ""
    echo "示例:"
    echo "  $0 conservative large_questions.md output        # 大文件安全处理"
    echo "  $0 balanced vue_questions.md output             # 标准处理"
    echo "  $0 aggressive small_questions.md output         # 快速处理"
    echo "  $0 test single_question.md test_output          # 测试单个问题"
    echo "  $0 custom questions.md output 2-4 8-12          # 自定义: 2-4个问题/批，8-12分钟间隔"
    echo "  $0 balanced vue_questions.md output --skip-existing  # 跳过已完成的问题"
    echo ""
    echo "注意事项:"
    echo "  - 保守模式适合100+问题的大文件，可以有效避免API限制"
    echo "  - 使用 --skip-existing 可以跳过已转换的问题，显著加速重复运行"
    echo "  - 当批次内所有问题都已存在时，自动跳过等待，立即处理下一批次"
    echo "  - 处理会自动保存进度，可以随时中断和继续"
    echo "  - 生成的日志文件在输出目录中的 batch_processing.log"
    echo "  - 进度文件 batch_progress.json 记录处理状态"
}

# 获取预估时间
estimate_time() {
    local mode=$1
    local input_file=$2
    
    # 简单估算问题数量（每个---大概对应一个问题）
    local question_count=$(grep -c "^---" "$input_file" 2>/dev/null || echo "未知")
    
    if [ "$question_count" != "未知" ]; then
        case $mode in
            "conservative")
                local avg_batch=2.5
                local avg_interval=15
                ;;
            "balanced")
                local avg_batch=4
                local avg_interval=10
                ;;
            "aggressive")
                local avg_batch=6.5
                local avg_interval=5
                ;;
            "test")
                local avg_batch=1
                local avg_interval=0.75
                ;;
            *)
                local avg_batch=4
                local avg_interval=10
                ;;
        esac
        
        local batches=$(echo "scale=0; ($question_count + $avg_batch - 1) / $avg_batch" | bc -l 2>/dev/null || echo "1")
        local total_minutes=$(echo "scale=1; $batches * $avg_interval" | bc -l 2>/dev/null || echo "未知")
        
        echo "预估: $question_count 个问题, $batches 个批次, 约 ${total_minutes} 分钟"
    else
        echo "无法估算处理时间（文件格式检测失败）"
    fi
}

# 主函数
main() {
    if [ $# -lt 3 ]; then
        show_help
        exit 1
    fi
    
    local mode=$1
    local input_file=$2
    local output_dir=$3
    
    # 检查是否有 --skip-existing 参数
    local skip_existing=""
    local additional_params=""
    
    # 检查所有参数中是否包含 --skip-existing
    for arg in "$@"; do
        if [ "$arg" = "--skip-existing" ]; then
            skip_existing="--skip-existing"
            additional_params="$additional_params $skip_existing"
            print_info "启用跳过已存在问题模式"
            break
        fi
    done
    
    # 检查输入文件
    if [ ! -f "$input_file" ]; then
        print_error "输入文件不存在: $input_file"
        exit 1
    fi
    
    # 检查虚拟环境
    check_venv
    
    # 确定处理参数
    local batch_size=""
    local interval=""
    
    case $mode in
        "conservative")
            batch_size="2-3"
            interval="10-20"
            print_info "使用保守模式: 每批2-3个问题，间隔10-20分钟"
            ;;
        "balanced")
            batch_size="3-5"
            interval="5-10"
            print_info "使用平衡模式: 每批3-5个问题，间隔5-10分钟"
            ;;
        "aggressive")
            batch_size="5-8"
            interval="2-8"
            print_info "使用激进模式: 每批5-8个问题，间隔2-8分钟"
            ;;
        "test")
            batch_size="1-1"
            interval="0.5-1"
            print_info "使用测试模式: 每批1个问题，间隔0.5-1分钟"
            ;;
        "custom")
            if [ $# -lt 5 ]; then
                print_error "自定义模式需要额外参数: <批次大小> <间隔时间>"
                echo "示例: $0 custom questions.md output 2-4 8-12"
                exit 1
            fi
            batch_size=$4
            interval=$5
            print_info "使用自定义模式: 每批${batch_size}个问题，间隔${interval}分钟"
            ;;
        *)
            print_error "未知模式: $mode"
            show_help
            exit 1
            ;;
    esac
    
    # 显示预估信息
    print_info "$(estimate_time $mode $input_file)"
    
    # 询问确认
    echo ""
    read -p "是否继续处理? [y/N]: " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "用户取消处理"
        exit 0
    fi
    
    # 开始处理
    print_success "开始批量处理..."
    echo ""
    
    # 构建 Python 脚本命令
    local python_cmd="python3 question_to_speech_batch_safe.py \"$input_file\" \"$output_dir\" \"$batch_size\" \"$interval\"$additional_params"
    
    if [ -n "$skip_existing" ]; then
        print_info "使用跳过模式: 已存在的问题将被跳过，批次内全部存在时不等待直接进入下一批次"
    fi
    
    print_info "执行命令: $python_cmd"
    echo ""
    
    # 执行 Python 脚本
    eval $python_cmd
    
    if [ $? -eq 0 ]; then
        print_success "批量处理完成!"
        print_info "输出目录: $output_dir"
        print_info "日志文件: $output_dir/batch_processing.log"
        print_info "进度文件: $output_dir/batch_progress.json"
    else
        print_error "批量处理失败，请检查日志文件"
        exit 1
    fi
}

# 运行主函数
main "$@"