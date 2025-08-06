"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "@/components/ui/use-toast";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useDropzone } from "react-dropzone";
import {
    Mic,
    MicOff,
    Send,
    Image as ImageIcon,
    X,
    Bot,
    User,
    Loader2,
    Brain,
    Settings
} from "lucide-react";

interface Message {
    id: string;
    text: string;
    from: "user" | "fusion";
    agent?: string;
    timestamp: Date;
    metadata?: {
        confidence?: number;
        pattern_type?: string;
        suggested_agents?: string[];
        orchestrator_used?: boolean;
    };
}

interface VoiceRecording {
    blob: Blob;
    url: string;
}

interface ImageAttachment {
    file: File;
    url: string;
    name: string;
}

export default function FusionChat() {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [voiceRecording, setVoiceRecording] = useState<VoiceRecording | null>(null);
    const [imageAttachments, setImageAttachments] = useState<ImageAttachment[]>([]);
    const [useOrchestrator, setUseOrchestrator] = useState(true);

    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const eventSourceRef = useRef<EventSource | null>(null);

    // Auto-scroll to bottom of messages
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Helper function to format agent names for display in messages
    const formatAgentName = (agentKey: string): string => {
        const agentNames: { [key: string]: string } = {
            "vp_design": "VP of Design",
            "creative_director": "Creative Director",
            "evaluator": "Quality Evaluator",
            "principal_designer": "Principal Designer",
            "ai_native_ux_designer": "AI-Native UX Designer",
            "ai_interaction_designer": "AI Interaction Designer",
            "design_judgment_engine": "Design Judgment Engine",
            "vp_of_product": "VP of Product",
            "product_navigator": "Product Navigator",
            "content_designer": "Content Designer",
            "deck_narrator": "Deck Narrator",
            "design_technologist": "Design Technologist",
            "dispatcher_agent": "Dispatcher Agent",
            "feedback_amplifier": "Feedback Amplifier",
            "market_analyst": "Market Analyst",
            "pattern_refiner": "Pattern Refiner",
            "portfolio_editor": "Portfolio Editor",
            "product_historian": "Product Historian",
            "prompt_master": "Prompt Master",
            "reflection_agent": "Reflection Agent",
            "research_summarizer": "Research Summarizer",
            "strategy_archivist": "Strategy Archivist",
            "strategy_pilot": "Strategy Pilot",
            "workflow_optimizer": "Workflow Optimizer",
            "component_librarian": "Component Librarian"
        };
        return agentNames[agentKey] || agentKey.split('_').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    };

    // Voice recording functionality
    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunksRef.current.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
                const audioUrl = URL.createObjectURL(audioBlob);
                setVoiceRecording({ blob: audioBlob, url: audioUrl });

                // Stop all tracks to release microphone
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setIsRecording(true);
        } catch (error) {
            toast({
                title: "Recording Error",
                description: "Could not access microphone. Please check permissions.",
                variant: "destructive",
            });
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    const clearVoiceRecording = () => {
        if (voiceRecording) {
            URL.revokeObjectURL(voiceRecording.url);
            setVoiceRecording(null);
        }
    };

    // Image drop zone
    const onDrop = useCallback((acceptedFiles: File[]) => {
        const newAttachments = acceptedFiles.map(file => ({
            file,
            url: URL.createObjectURL(file),
            name: file.name
        }));

        setImageAttachments(prev => [...prev, ...newAttachments]);
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp']
        },
        multiple: true,
        noClick: true // Only allow drop, not click
    });

    const removeImageAttachment = (index: number) => {
        const attachment = imageAttachments[index];
        URL.revokeObjectURL(attachment.url);
        setImageAttachments(prev => prev.filter((_, i) => i !== index));
    };

    // Send prompt to Fusion API
    const sendPrompt = async () => {
        if (!input.trim() && !voiceRecording && imageAttachments.length === 0) {
            return;
        }

        const userMessage: Message = {
            id: Date.now().toString(),
            text: input || "[Voice/Image message]",
            from: "user",
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);

        try {
            // Prepare request for Fusion API
            let requestInput = input;

            // Add voice/image context to text input
            if (voiceRecording) {
                requestInput += "\n[Voice recording attached - please acknowledge this voice input]";
            }
            if (imageAttachments.length > 0) {
                requestInput += `\n[${imageAttachments.length} image(s) attached: ${imageAttachments.map(img => img.name).join(", ")} - please acknowledge these images]`;
            }

            // Send to Fusion API using the /run/auto endpoint for intelligent agent selection
            const response = await fetch("http://localhost:8000/run/auto", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    input: requestInput || "Please provide a design recommendation",
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            // Create Fusion response message
            const fusionMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: result.output || "No response from agent",
                from: "fusion",
                agent: result.agent,
                timestamp: new Date(),
                metadata: {
                    confidence: 0.9,
                    pattern_type: "auto_selected",
                    suggested_agents: [result.agent],
                    orchestrator_used: result.auto_selected || false,
                    rewritten_prompt: result.rewritten_prompt,
                },
            };

            setMessages(prev => [...prev, fusionMessage]);

            // Show success toast with agent info
            toast({
                title: "Response from Fusion",
                description: `Auto-selected ${formatAgentName(result.agent)} responded successfully!`,
            });

        } catch (error) {
            console.error("Error sending prompt:", error);

            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: `Error: ${error instanceof Error ? error.message : "Failed to send prompt"}`,
                from: "fusion",
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, errorMessage]);

            toast({
                title: "Error",
                description: "Failed to send prompt to Fusion",
                variant: "destructive",
            });
        } finally {
            setIsLoading(false);
            setInput("");
            clearVoiceRecording();
            setImageAttachments([]);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendPrompt();
        }
    };

    return (
        <div className="h-screen flex flex-col bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
            {/* Header */}
            <div className="border-b bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm p-4">
                <div className="flex items-center justify-between max-w-4xl mx-auto">
                    <div className="flex items-center space-x-3">
                        <Brain className="h-8 w-8 text-blue-600" />
                        <div>
                            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                                Fusion v15
                            </h1>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                                AI Agentic Operating System
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center space-x-3">
                        {/* Auto-routing indicator */}
                        <div className="flex items-center space-x-2">
                            <div className="flex items-center space-x-1">
                                <Brain className="h-4 w-4 text-blue-600" />
                                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                    Auto-Agent Selection
                                </span>
                            </div>
                        </div>

                        {/* Orchestrator Toggle */}
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setUseOrchestrator(!useOrchestrator)}
                            className={useOrchestrator ? "bg-blue-50 border-blue-200" : ""}
                        >
                            <Settings className="h-4 w-4 mr-1" />
                            Orchestrator {useOrchestrator ? "ON" : "OFF"}
                        </Button>
                    </div>
                </div>
            </div>

            {/* Messages Container */}
            <div
                {...getRootProps()}
                className={`flex-1 overflow-y-auto p-4 ${isDragActive ? "bg-blue-50 dark:bg-blue-900/20" : ""}`}
            >
                <div className="max-w-4xl mx-auto space-y-4">
                    {messages.length === 0 && (
                        <Card className="p-8 text-center border-dashed">
                            <CardContent>
                                <Brain className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                                    Welcome to Fusion v15
                                </h3>
                                <p className="text-gray-500 dark:text-gray-400">
                                    Start a conversation with our AI agents. Type a message, record voice, or drop images.
                                </p>
                            </CardContent>
                        </Card>
                    )}

                    {messages.map((message) => (
                        <div
                            key={message.id}
                            className={`flex ${message.from === "user" ? "justify-end" : "justify-start"}`}
                        >
                            <Card
                                className={`max-w-[80%] ${message.from === "user"
                                    ? "bg-blue-600 text-white border-blue-600"
                                    : "bg-white dark:bg-slate-800 border-gray-200 dark:border-slate-700"
                                    }`}
                            >
                                <CardContent className="p-4">
                                    <div className="flex items-start space-x-3">
                                        <div className="flex-shrink-0">
                                            {message.from === "user" ? (
                                                <User className="h-6 w-6" />
                                            ) : (
                                                <Bot className="h-6 w-6 text-blue-600" />
                                            )}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            {message.agent && (
                                                <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                                                    {message.agent}
                                                    {message.metadata?.orchestrator_used && (
                                                        <span className="ml-2 px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs">
                                                            Enhanced
                                                        </span>
                                                    )}
                                                </div>
                                            )}
                                            <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                                            {message.metadata && (
                                                <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                                                    {message.metadata.confidence && (
                                                        <span>Confidence: {(message.metadata.confidence * 100).toFixed(0)}%</span>
                                                    )}
                                                    {message.metadata.pattern_type && (
                                                        <span className="ml-2">Pattern: {message.metadata.pattern_type}</span>
                                                    )}
                                                </div>
                                            )}
                                            <div className="text-xs text-gray-400 mt-1">
                                                {message.timestamp.toLocaleTimeString()}
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="flex justify-start">
                            <Card className="bg-white dark:bg-slate-800">
                                <CardContent className="p-4">
                                    <div className="flex items-center space-x-3">
                                        <Bot className="h-6 w-6 text-blue-600" />
                                        <div className="flex items-center space-x-2">
                                            <Loader2 className="h-4 w-4 animate-spin" />
                                            <span className="text-sm text-gray-500">Fusion is thinking...</span>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {isDragActive && (
                    <div className="fixed inset-0 bg-blue-500/10 border-2 border-dashed border-blue-400 flex items-center justify-center pointer-events-none">
                        <div className="text-center">
                            <ImageIcon className="h-12 w-12 mx-auto text-blue-500 mb-2" />
                            <p className="text-lg font-medium text-blue-700">Drop images here</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Input Area */}
            <div className="border-t bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm p-4">
                <div className="max-w-4xl mx-auto">
                    {/* Attachments Preview */}
                    {(voiceRecording || imageAttachments.length > 0) && (
                        <div className="mb-3 flex flex-wrap gap-2">
                            {voiceRecording && (
                                <div className="flex items-center space-x-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-2">
                                    <Mic className="h-4 w-4 text-blue-600" />
                                    <span className="text-sm">Voice recording</span>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={clearVoiceRecording}
                                        className="h-6 w-6 p-0"
                                    >
                                        <X className="h-3 w-3" />
                                    </Button>
                                </div>
                            )}

                            {imageAttachments.map((attachment, index) => (
                                <div key={index} className="flex items-center space-x-2 bg-green-50 dark:bg-green-900/20 rounded-lg p-2">
                                    <ImageIcon className="h-4 w-4 text-green-600" />
                                    <span className="text-sm">{attachment.name}</span>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => removeImageAttachment(index)}
                                        className="h-6 w-6 p-0"
                                    >
                                        <X className="h-3 w-3" />
                                    </Button>
                                </div>
                            ))}
                        </div>
                    )}

                    <div className="flex space-x-2">
                        <div className="flex-1">
                            <Textarea
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="Type your prompt here... (Shift+Enter for new line)"
                                className="min-h-[60px] resize-none rounded-2xl border-gray-200 dark:border-slate-700"
                                disabled={isLoading}
                            />
                            <input {...getInputProps()} />
                        </div>

                        <div className="flex flex-col space-y-2">
                            <Button
                                variant="outline"
                                size="icon"
                                onClick={isRecording ? stopRecording : startRecording}
                                className={`rounded-xl ${isRecording ? "bg-red-50 border-red-200 text-red-600" : ""}`}
                                disabled={isLoading}
                            >
                                {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                            </Button>

                            <Button
                                onClick={sendPrompt}
                                disabled={isLoading || (!input.trim() && !voiceRecording && imageAttachments.length === 0)}
                                className="rounded-xl bg-blue-600 hover:bg-blue-700"
                            >
                                {isLoading ? (
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                ) : (
                                    <Send className="h-4 w-4" />
                                )}
                            </Button>
                        </div>
                    </div>

                    <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
                        Drop images anywhere • Hold to record voice • Enter to send
                    </div>
                </div>
            </div>
        </div>
    );
}