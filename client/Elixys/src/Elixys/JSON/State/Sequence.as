package Elixys.JSON.State
{
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class Sequence extends JSONObject
	{
		// Constructor
		public function Sequence(data:String = null, existingcontent:Object = null)
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
			return "sequence";
		}

		// Data wrappers
		public function get Metadata():SequenceMetadata
		{
			// Parse the metadata
			if (m_pMetadata == null)
			{
				m_pMetadata = new SequenceMetadata(null, super.flash_proxy::getProperty("metadata"));
			}
			return m_pMetadata;
		}
		public function get Components():Array
		{
			// Parse the components
			if (m_pComponents == null)
			{
				m_pComponents = new Array();
				var pComponents:Array = super.flash_proxy::getProperty("components");
				for each (var pComponentObject:Object in pComponents)
				{
					m_pComponents.push(new SequenceComponent(null, pComponentObject));
				}
			}
			return m_pComponents;
		}

		// Sequence comparison function.  Returns true if the sequences are equal, false otherwise.
		public static function CompareSequences(pSequenceA:Sequence, pSequenceB:Sequence):Boolean
		{
			if (!SequenceMetadata.CompareSequenceMetadata(pSequenceA.Metadata, pSequenceB.Metadata))
			{
				return false;
			}
			if (!SequenceComponent.CompareSequenceComponentArrays(pSequenceA.Components, pSequenceB.Components))
			{
				return false;
			}
			return true;
		}

		// State components
		private var m_pMetadata:SequenceMetadata;
		private var m_pComponents:Array;
	}
}
