import os
import sys
import heapq
import time
def _reverse_key(key):
    try:
        return -float(key)
    except (ValueError, TypeError):
        return tuple(-ord(c) for c in key)
def _negate_key(key, k_col):
    try:
        return -float(key)
    except (ValueError, TypeError):
        return tuple(-ord(c) for c in key)
def get_key_from_line(line, c_idx):
    start = 0
    for _ in range(c_idx):
        pos = line.find(',', start)
        if pos == -1:
            return ""
        start = pos + 1
    end = line.find(',', start)
    return line[start:end] if end != -1 else line[start:].strip()
def normalize_line(line):
    try:
        parts = line.split(',', 3)
        if len(parts) >= 2:
            parts[1] = str(int(parts[1]))
        return ','.join(parts)
    except:
        pass
    return line
def sort_ext(in_path="L5.csv", k_col=1, ch_mb=50, reverse=False, callback=None):
    ch_bytes = ch_mb * 1024 * 1024
    tmp_dir = "./temp_chunks"
    if os.path.exists(tmp_dir):
        import shutil
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)

    tmp_files = []
    print("External Sort | Key: col[%d] | Chunk: %d MB | Reverse: %s..." % (k_col, ch_mb, reverse))
    sys.stdout.flush()

    total_bytes = os.path.getsize(in_path)
    total_rows = 0
    t_s = time.time()
    progress_step = total_bytes // 200 + 1

    with open(in_path, "r", encoding="utf-8-sig", buffering=1 << 20) as f_in:
        next(f_in)
        buf = []
        cur_b = 0
        c_idx = 0
        bytes_processed = 0

        for line in f_in:
            line = line.strip()
            if not line:
                continue
            norm_line = normalize_line(line)
            buf.append(norm_line)
            row_bytes = len(norm_line) + 1
            cur_b += row_bytes
            bytes_processed += row_bytes
            total_rows += 1

            if bytes_processed % progress_step == 0:
                pct = min(40, int((bytes_processed / total_bytes) * 40))
                if callback: callback(pct)

            if cur_b >= ch_bytes:
                buf.sort(key=lambda x: get_key_from_line(x, k_col), reverse=reverse)
                tp = os.path.join(tmp_dir, "chunk_%d.tmp" % c_idx)
                with open(tp, "w", encoding="utf-8-sig", buffering=1 << 20) as f_out:
                    f_out.write("\n".join(buf))
                    f_out.write("\n")
                tmp_files.append(tp)
                buf.clear()
                cur_b = 0
                c_idx += 1

        if buf:
            buf.sort(key=lambda x: get_key_from_line(x, k_col), reverse=reverse)
            tp = os.path.join(tmp_dir, "chunk_%d.tmp" % c_idx)
            with open(tp, "w", encoding="utf-8-sig", buffering=1 << 20) as f_out:
                f_out.write("\n".join(buf))
                f_out.write("\n")
            tmp_files.append(tp)
            buf.clear()

    if callback: callback(40)
    print("Split phase complete. Starting merge...")
    sys.stdout.flush()

    t_e1 = time.time()
    print("Split time: %.2fs | Chunks: %d" % (t_e1 - t_s, len(tmp_files)))
    sys.stdout.flush()

    t_m_s = time.time()
    out_p = os.path.join(os.path.dirname(in_path), "sorted_py.txt")
    heap = []
    fds = []

    for i, p in enumerate(tmp_files):
        f = open(p, "r", encoding="utf-8-sig", buffering=1 << 20)
        fds.append(f)
        line = f.readline()
        if line:
            line = line.strip()
            key = get_key_from_line(line, k_col)
            entry = (-ord(key[0]) if (reverse and key) else key, i, line) if not reverse else (key, i, line)
            heapq.heappush(heap, (key, i, line) if not reverse else (key, i, line))

    if reverse:
        heap_data = [(get_key_from_line(item[2], k_col), item[1], item[2]) for item in heap]
        heap = [(_negate_key(k, k_col), i, l) for k, i, l in heap_data]
        heapq.heapify(heap)

    heap = []
    fds2 = []
    for i, p in enumerate(tmp_files):
        fds[i].seek(0)

    for fd in fds:
        fd.close()
    fds = []

    for i, p in enumerate(tmp_files):
        f = open(p, "r", encoding="utf-8-sig", buffering=1 << 20)
        fds2.append(f)
        line = f.readline()
        if line:
            line = line.strip()
            key = get_key_from_line(line, k_col)
            if reverse:
                heapq.heappush(heap, (_reverse_key(key), i, line))
            else:
                heapq.heappush(heap, (key, i, line))

    progress_step2 = total_rows // 200 + 1

    with open(out_p, "w", encoding="utf-8-sig", buffering=1 << 20) as out_f:
        rows_written = 0
        while heap:
            _, f_id, line = heapq.heappop(heap)
            out_f.write(line)
            out_f.write("\n")
            rows_written += 1

            if rows_written % progress_step2 == 0:
                pct = 40 + min(60, int((rows_written / total_rows) * 60))
                if callback: callback(pct)

            next_line = fds2[f_id].readline()
            if next_line:
                next_line = next_line.strip()
                key = get_key_from_line(next_line, k_col)
                if reverse:
                    heapq.heappush(heap, (_reverse_key(key), f_id, next_line))
                else:
                    heapq.heappush(heap, (key, f_id, next_line))

    for f in fds2:
        f.close()

    if callback: callback(100)
    sys.stdout.flush()

    t_e2 = time.time()
    print("Merge time: %.2fs" % (t_e2 - t_m_s))
    print("Total time: %.2fs" % ((t_e1 - t_s) + (t_e2 - t_m_s)))
    print("Output: sorted_py.txt")
    print("Cleaning temp files...")

    import shutil
    try:
        shutil.rmtree(tmp_dir)
    except:
        pass
    print("Done.")
if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "L5.csv"
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    cs = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    rev = sys.argv[4].lower() == "true" if len(sys.argv) > 4 else False
    sort_ext(inp, k, cs, rev)