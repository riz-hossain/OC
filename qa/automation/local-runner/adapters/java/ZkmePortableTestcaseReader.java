import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class ZkmePortableTestcaseReader {
    public static void main(String[] args) throws Exception {
        if (args.length == 0) {
            System.err.println("Usage: java ZkmePortableTestcaseReader <portable-testcase.json> [...]");
            System.exit(2);
        }
        int failures = 0;
        for (String arg : args) {
            try {
                PortableCase tc = read(Path.of(arg));
                System.out.println(tc.id + " | " + tc.title + " | steps=" + tc.steps.size());
                for (PortableStep step : tc.steps) {
                    System.out.println("  - " + step.id + " [" + step.adapter + "] " + step.intent);
                }
            } catch (Exception exc) {
                failures += 1;
                System.err.println(arg + ": " + exc.getMessage());
            }
        }
        if (failures > 0) {
            System.exit(1);
        }
    }

    public static PortableCase read(Path path) throws IOException {
        Object parsed = new JsonParser(Files.readString(path, StandardCharsets.UTF_8)).parse();
        if (!(parsed instanceof Map)) {
            throw new IllegalArgumentException("root JSON value must be an object");
        }
        Map<?, ?> root = (Map<?, ?>) parsed;
        String schema = stringValue(root.get("schemaVersion"));
        if (!"zkme.portable-testcase.v1".equals(schema)) {
            throw new IllegalArgumentException("schemaVersion must be zkme.portable-testcase.v1");
        }
        String id = requiredString(root, "id");
        String title = requiredString(root, "title");
        Object rawSteps = root.get("steps");
        if (!(rawSteps instanceof List)) {
            throw new IllegalArgumentException("steps must be an array");
        }
        List<PortableStep> steps = new ArrayList<>();
        int index = 1;
        for (Object item : (List<?>) rawSteps) {
            if (!(item instanceof Map)) {
                throw new IllegalArgumentException("step " + index + " must be an object");
            }
            Map<?, ?> step = (Map<?, ?>) item;
            steps.add(new PortableStep(
                stringValue(valueOrDefault(step, "id", "step-" + index)),
                stringValue(valueOrDefault(step, "adapter", "manual")),
                stringValue(valueOrDefault(step, "intent", valueOrDefault(step, "action", "Step " + index))),
                stringValue(valueOrDefault(step, "expected", ""))
            ));
            index += 1;
        }
        return new PortableCase(id, title, steps);
    }

    private static String requiredString(Map<?, ?> map, String key) {
        String value = stringValue(map.get(key));
        if (value.isBlank()) {
            throw new IllegalArgumentException("missing required field: " + key);
        }
        return value;
    }

    private static String stringValue(Object value) {
        return value == null ? "" : String.valueOf(value);
    }

    private static Object valueOrDefault(Map<?, ?> map, String key, Object fallback) {
        Object value = map.get(key);
        return value == null ? fallback : value;
    }

    public static final class PortableCase {
        public final String id;
        public final String title;
        public final List<PortableStep> steps;

        public PortableCase(String id, String title, List<PortableStep> steps) {
            this.id = id;
            this.title = title;
            this.steps = steps;
        }
    }

    public static final class PortableStep {
        public final String id;
        public final String adapter;
        public final String intent;
        public final String expected;

        public PortableStep(String id, String adapter, String intent, String expected) {
            this.id = id;
            this.adapter = adapter;
            this.intent = intent;
            this.expected = expected;
        }
    }

    private static final class JsonParser {
        private final String text;
        private int offset = 0;

        JsonParser(String text) {
            this.text = text;
        }

        Object parse() {
            Object value = parseValue();
            skipWhitespace();
            if (offset != text.length()) {
                throw error("unexpected trailing content");
            }
            return value;
        }

        private Object parseValue() {
            skipWhitespace();
            if (offset >= text.length()) {
                throw error("unexpected end of JSON");
            }
            char ch = text.charAt(offset);
            if (ch == '{') return parseObject();
            if (ch == '[') return parseArray();
            if (ch == '"') return parseString();
            if (ch == 't') return parseLiteral("true", Boolean.TRUE);
            if (ch == 'f') return parseLiteral("false", Boolean.FALSE);
            if (ch == 'n') return parseLiteral("null", null);
            if (ch == '-' || Character.isDigit(ch)) return parseNumber();
            throw error("unexpected character: " + ch);
        }

        private Map<String, Object> parseObject() {
            expect('{');
            Map<String, Object> object = new LinkedHashMap<>();
            skipWhitespace();
            if (peek('}')) {
                offset += 1;
                return object;
            }
            while (true) {
                String key = parseString();
                skipWhitespace();
                expect(':');
                object.put(key, parseValue());
                skipWhitespace();
                if (peek('}')) {
                    offset += 1;
                    return object;
                }
                expect(',');
            }
        }

        private List<Object> parseArray() {
            expect('[');
            List<Object> array = new ArrayList<>();
            skipWhitespace();
            if (peek(']')) {
                offset += 1;
                return array;
            }
            while (true) {
                array.add(parseValue());
                skipWhitespace();
                if (peek(']')) {
                    offset += 1;
                    return array;
                }
                expect(',');
            }
        }

        private String parseString() {
            expect('"');
            StringBuilder builder = new StringBuilder();
            while (offset < text.length()) {
                char ch = text.charAt(offset++);
                if (ch == '"') {
                    return builder.toString();
                }
                if (ch == '\\') {
                    if (offset >= text.length()) throw error("bad escape");
                    char escaped = text.charAt(offset++);
                    switch (escaped) {
                        case '"': builder.append('"'); break;
                        case '\\': builder.append('\\'); break;
                        case '/': builder.append('/'); break;
                        case 'b': builder.append('\b'); break;
                        case 'f': builder.append('\f'); break;
                        case 'n': builder.append('\n'); break;
                        case 'r': builder.append('\r'); break;
                        case 't': builder.append('\t'); break;
                        case 'u':
                            if (offset + 4 > text.length()) throw error("bad unicode escape");
                            builder.append((char) Integer.parseInt(text.substring(offset, offset + 4), 16));
                            offset += 4;
                            break;
                        default:
                            throw error("bad escape: " + escaped);
                    }
                } else {
                    builder.append(ch);
                }
            }
            throw error("unterminated string");
        }

        private Object parseNumber() {
            int start = offset;
            if (peek('-')) offset += 1;
            while (offset < text.length() && Character.isDigit(text.charAt(offset))) offset += 1;
            if (peek('.')) {
                offset += 1;
                while (offset < text.length() && Character.isDigit(text.charAt(offset))) offset += 1;
            }
            if (offset < text.length() && (text.charAt(offset) == 'e' || text.charAt(offset) == 'E')) {
                offset += 1;
                if (offset < text.length() && (text.charAt(offset) == '+' || text.charAt(offset) == '-')) offset += 1;
                while (offset < text.length() && Character.isDigit(text.charAt(offset))) offset += 1;
            }
            String raw = text.substring(start, offset);
            return raw.contains(".") || raw.contains("e") || raw.contains("E") ? Double.parseDouble(raw) : Long.parseLong(raw);
        }

        private Object parseLiteral(String literal, Object value) {
            if (!text.startsWith(literal, offset)) {
                throw error("expected " + literal);
            }
            offset += literal.length();
            return value;
        }

        private void expect(char expected) {
            skipWhitespace();
            if (offset >= text.length() || text.charAt(offset) != expected) {
                throw error("expected '" + expected + "'");
            }
            offset += 1;
        }

        private boolean peek(char expected) {
            return offset < text.length() && text.charAt(offset) == expected;
        }

        private void skipWhitespace() {
            while (offset < text.length() && Character.isWhitespace(text.charAt(offset))) {
                offset += 1;
            }
        }

        private IllegalArgumentException error(String message) {
            return new IllegalArgumentException(message + " at offset " + offset);
        }
    }
}
