package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class State extends JSONObject
	{
		// Constructor
		public function State(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type() != null) && (Type() != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Data wrappers
		public function Type():String
		{
			return super.flash_proxy::getProperty("type");
		}
		public function User():Elixys.Objects.User
		{
			// Parse the user
			if (m_pUser == null)
			{
				m_pUser = new Elixys.Objects.User(null, super.flash_proxy::getProperty("user"));
			}
			return m_pUser;
		}
		public function ServerState():Elixys.Objects.ServerState
		{
			// Parse the server state
			if (m_pServerState == null)
			{
				m_pServerState = new Elixys.Objects.ServerState(null, super.flash_proxy::getProperty("serverstate"));
			}
			return m_pServerState;
		}
		public function ClientState():String
		{
			return super.flash_proxy::getProperty("clientstate");
		}
		
		// Type
		static public var TYPE:String = "state";
		
		// State components
		private var m_pUser:Elixys.Objects.User;
		private var m_pServerState:Elixys.Objects.ServerState;
		private var m_pClientDetailsHome:Elixys.Objects.StateHome;
		private var m_pClientDetailsSelect:Elixys.Objects.StateSelect;
		private var m_pClientDetailsView:Elixys.Objects.StateView;
	}
}
