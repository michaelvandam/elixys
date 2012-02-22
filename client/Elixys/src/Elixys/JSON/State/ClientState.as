package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;

	import flash.utils.flash_proxy;
	
	public class ClientState extends JSONObject
	{
		// Constructor
		public function ClientState(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type != null) && (Type != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Static type
		public static function get TYPE():String
		{
			return "clientstate";
		}
		
		// Data wrappers
		public function get PromptState():Elixys.JSON.State.PromptState
		{
			// Parse the prompt state
			if (m_pPromptState == null)
			{
				m_pPromptState = new Elixys.JSON.State.PromptState(null, super.flash_proxy::getProperty("prompt"));
			}
			return m_pPromptState;
		}
		public function get Screen():String
		{
			return super.flash_proxy::getProperty("screen");
		}
		public function get SequenceID():uint
		{
			return super.flash_proxy::getProperty("sequenceid");
		}
		public function get ComponentID():uint
		{
			return super.flash_proxy::getProperty("componentid");
		}
		public function get LastSelectScreen():String
		{
			return super.flash_proxy::getProperty("lastselectscreen");
		}
		
		// State components
		private var m_pPromptState:Elixys.JSON.State.PromptState;
	}
}
